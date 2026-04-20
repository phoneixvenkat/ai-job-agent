import imaplib
import email
import os
import re
from email.header import decode_header
from database.mysql_db import (
    get_connection, update_application_status,
    get_processed_message_ids, mark_message_processed,
)
from mysql.connector import Error
from backend.utils.logger import get_logger

log = get_logger("email_agent")

_llm = None
_processed_ids: set | None = None   # lazy-loaded from DB once per process

def _get_llm():
    global _llm
    if _llm is None:
        from langchain_ollama import ChatOllama
        _llm = ChatOllama(model="llama3", base_url="http://localhost:11434", temperature=0)
    return _llm

def _load_processed_ids() -> set:
    global _processed_ids
    if _processed_ids is None:
        _processed_ids = get_processed_message_ids()
        log.info("Loaded %d processed message-ids from DB", len(_processed_ids))
    return _processed_ids


# ── IMAP config ───────────────────────────────────────
_IMAP_CONFIGS = {
    "gmail":   {"host": "imap.gmail.com",        "port": 993},
    "outlook": {"host": "outlook.office365.com", "port": 993},
    "yahoo":   {"host": "imap.mail.yahoo.com",   "port": 993},
}

INTERVIEW_KEYWORDS = [
    "interview", "pleased to", "excited to", "next steps",
    "schedule", "call with", "move forward", "invite you",
    "speak with", "meet with", "phone screen", "video call",
]
REJECTED_KEYWORDS = [
    "unfortunately", "not moving forward", "other candidates",
    "not a fit", "regret to", "decided to", "not selected",
    "will not be", "position has been filled", "not proceed",
]


# ── 1. classify_email — returns confidence dict ───────
def classify_email(subject: str, body: str) -> dict:
    """Returns {"status": "INTERVIEW"|"REJECTED"|"NO_RESPONSE", "confidence": float}"""
    text = (subject + " " + body).lower()
    if any(kw in text for kw in INTERVIEW_KEYWORDS):
        return {"status": "INTERVIEW",    "confidence": 0.90}
    if any(kw in text for kw in REJECTED_KEYWORDS):
        return {"status": "REJECTED",     "confidence": 0.88}

    # LLM fallback for ambiguous emails
    llm_result = _classify_with_llm(subject, body)
    if llm_result and llm_result != "NO_RESPONSE":
        return {"status": llm_result, "confidence": 0.67}
    return {"status": "NO_RESPONSE", "confidence": 0.50}


def _classify_with_llm(subject: str, body: str) -> str | None:
    from langchain_core.messages import HumanMessage
    prompt = (
        "Classify this email as exactly one of: INTERVIEW, REJECTED, NO_RESPONSE\n\n"
        f"Subject: {subject}\nBody (first 600 chars): {body[:600]}\n\n"
        "Reply with only the classification word."
    )
    try:
        response = _get_llm().invoke([HumanMessage(content=prompt)])
        result = response.content.strip().upper()
        if result in ("INTERVIEW", "REJECTED", "NO_RESPONSE"):
            return result
    except Exception:
        pass
    return None


# ── 2. _find_matching_application — multi-signal scoring ──
def _find_matching_application(
    subject: str, body: str, from_addr: str = ""
) -> tuple[int | None, float]:
    """
    Score each open application against the email.
    Returns (app_id, score) where score is 0-1, or (None, 0.0) if no match.
    """
    conn = get_connection()
    if not conn:
        return None, 0.0
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, org, title FROM applications "
            "WHERE status='applied' ORDER BY applied_at DESC LIMIT 100"
        )
        apps = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        return None, 0.0

    text = (subject + " " + body[:500]).lower()
    # extract sender domain e.g. "no-reply@greenhouse.io" → "greenhouse"
    sender_domain = ""
    m = re.search(r"@([\w.-]+)", from_addr)
    if m:
        parts = m.group(1).split(".")
        sender_domain = parts[-2] if len(parts) >= 2 else parts[0]

    best_id, best_score = None, 0.0
    for app in apps:
        score = 0.0
        org   = (app["org"] or "").lower()
        title = (app["title"] or "").lower()

        # (a) company name appears in email text
        if org and org in text:
            score += 0.60

        # (b) sender domain matches company name token
        if sender_domain and org:
            org_tokens = re.split(r"[\s\-_]+", org)
            if any(sender_domain in tok or tok in sender_domain for tok in org_tokens if len(tok) > 2):
                score += 0.25

        # (c) job title keywords in email text
        title_words = [w for w in re.split(r"\W+", title) if len(w) > 3]
        if title_words:
            hits = sum(1 for w in title_words if w in text)
            score += 0.15 * (hits / len(title_words))

        if score > best_score:
            best_score = score
            best_id = app["id"]

    if best_score >= 0.30:
        return best_id, round(best_score, 2)
    return None, 0.0


# ── 3. IMAP helpers ───────────────────────────────────
def connect_email(email_addr: str = None, password: str = None, provider: str = "gmail"):
    email_addr = email_addr or os.environ.get("EMAIL_ADDRESS", "")
    password   = password   or os.environ.get("EMAIL_PASSWORD", "")
    imap_host  = os.environ.get("IMAP_SERVER", _IMAP_CONFIGS.get(provider, {}).get("host", ""))
    imap_port  = int(os.environ.get("IMAP_PORT", _IMAP_CONFIGS.get(provider, {}).get("port", 993)))

    if not email_addr or not password:
        log.error("Email credentials missing — set EMAIL_ADDRESS and EMAIL_PASSWORD env vars")
        return None
    try:
        mail = imaplib.IMAP4_SSL(imap_host, imap_port)
        mail.login(email_addr, password)
        log.info("Connected to %s (%s)", provider, imap_host)
        return mail
    except Exception as e:
        log.error("IMAP connection failed: %s", e)
        return None


def fetch_recent_emails(mail, limit: int = 30) -> list:
    try:
        mail.select("inbox")
        _, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()[-limit:]
        emails = []
        for eid in reversed(email_ids):
            try:
                _, msg_data = mail.fetch(eid, "(RFC822)")
                for part in msg_data:
                    if not isinstance(part, tuple):
                        continue
                    msg = email.message_from_bytes(part[1])

                    subject_raw = decode_header(msg["Subject"] or "")[0][0]
                    subject = subject_raw.decode() if isinstance(subject_raw, bytes) else (subject_raw or "")
                    sender  = msg.get("From", "")
                    msg_id  = (msg.get("Message-ID") or "").strip()

                    body = ""
                    if msg.is_multipart():
                        for p in msg.walk():
                            if p.get_content_type() == "text/plain":
                                body = p.get_payload(decode=True).decode("utf-8", errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                    emails.append({
                        "from":       sender,
                        "subject":    subject,
                        "body":       body[:2000],
                        "message_id": msg_id,
                    })
            except Exception as e:
                log.warning("Skipping email: %s", e)
        return emails
    except Exception as e:
        log.error("fetch_recent_emails failed: %s", e)
        return []


def save_email_intel(data: dict):
    conn = get_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO email_intel
            (application_id, email_from, email_subject, email_body,
             classification, sender_name, company_info)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            data.get("application_id"),
            data.get("from", ""),
            data.get("subject", ""),
            data.get("body", "")[:2000],
            data.get("classification", ""),
            data.get("from", "")[:256],
            "",
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        log.error("save_email_intel failed: %s", e)


# ── 4. Main entry point ───────────────────────────────
def run_email_agent(
    email_addr: str = None, password: str = None, provider: str = "gmail"
) -> list:
    log.info("Email Agent starting")
    mail = connect_email(email_addr, password, provider)
    if not mail:
        return []

    emails  = fetch_recent_emails(mail, limit=30)
    seen    = _load_processed_ids()
    results = []

    for em in emails:
        msg_id = em.get("message_id", "")
        log.info("Received: [%s] %s", msg_id[:20] or "no-id", em["subject"][:60])

        # ── Deduplication ──
        if msg_id and msg_id in seen:
            log.info("  Skipping already-processed message-id: %s", msg_id[:40])
            continue

        classification = classify_email(em["subject"], em["body"])
        status     = classification["status"]
        confidence = classification["confidence"]
        log.info("  Classified: %s (confidence=%.2f)", status, confidence)

        if status == "NO_RESPONSE":
            # Still mark as processed so we don't re-scan it
            if msg_id:
                seen.add(msg_id)
                mark_message_processed(msg_id)
            continue

        app_id, match_score = _find_matching_application(
            em["subject"], em["body"], em["from"]
        )

        if app_id:
            new_status = "interview" if status == "INTERVIEW" else "rejected"
            update_application_status(app_id, new_status)
            log.info(
                "  DB updated: app #%d -> '%s' (match_score=%.2f)",
                app_id, new_status, match_score,
            )
        else:
            log.info("  No matching application found for this email")

        result = {
            **em,
            "classification":  status,
            "confidence":      confidence,
            "application_id":  app_id,
            "match_score":     match_score,
        }
        save_email_intel(result)
        results.append(result)

        # Mark as processed (in-memory + DB)
        if msg_id:
            seen.add(msg_id)
            mark_message_processed(msg_id)

    log.info("Email Agent done — %d actionable emails", len(results))
    return results
