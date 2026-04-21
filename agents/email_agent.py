import os
import re
import json
import email
import imaplib
from email.header import decode_header
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from database.mysql_db import (
    get_connection, update_application_status,
    get_all_applications, get_processed_message_ids, mark_message_processed,
)
from mysql.connector import Error
from backend.utils.logger import get_logger
log = get_logger('email_agent')

load_dotenv()

_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        from langchain_groq import ChatGroq
        _llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0,
        )
    return _llm


EMAIL_CONFIG = {
    "gmail":   {"imap_server": "imap.gmail.com",           "imap_port": 993},
    "outlook": {"imap_server": "outlook.office365.com",    "imap_port": 993},
}


def connect_email(email_addr: str, password: str, provider: str = "gmail"):
    try:
        config = EMAIL_CONFIG[provider]
        mail   = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
        mail.login(email_addr, password)
        log.info(f"Connected to {provider} inbox")
        return mail
    except Exception as e:
        log.error(f"Email connection error: {e}")
        return None


def fetch_recent_emails(mail, limit: int = 20) -> list:
    try:
        mail.select("inbox")
        _, messages = mail.search(None, "ALL")
        email_ids   = messages[0].split()[-limit:]
        emails      = []

        for eid in reversed(email_ids):
            _, msg_data = mail.fetch(eid, "(RFC822 UID)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg     = email.message_from_bytes(response_part[1])
                    subject = decode_header(msg["Subject"] or "")[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(errors="ignore")
                    sender  = msg.get("From", "")
                    msg_id  = msg.get("Message-ID", str(eid))
                    body    = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                    emails.append({
                        "message_id": msg_id,
                        "from":       sender,
                        "subject":    subject,
                        "body":       body[:2000],
                    })
        return emails
    except Exception as e:
        log.error(f"Fetch emails error: {e}")
        return []


def classify_email(email_data: dict) -> dict:
    prompt = f"""Classify this job application email.

From: {email_data['from']}
Subject: {email_data['subject']}
Body: {email_data['body'][:800]}

Classify as one of: interview, offer, rejection, assessment, followup, other

Return ONLY this JSON:
{{
    "classification": "<type>",
    "confidence": <0.0-1.0>,
    "company": "<name>",
    "sender_name": "<name>",
    "key_message": "<1 sentence>"
}}"""

    try:
        response = _get_llm().invoke([HumanMessage(content=prompt)])
        text     = re.sub(r'```json|```', '', response.content.strip()).strip()
        return json.loads(text)
    except Exception:
        return {"classification": "other", "confidence": 0.0, "company": "", "sender_name": "", "key_message": ""}


def _find_matching_application(from_addr: str, subject: str) -> dict | None:
    """Return the best-matching application for an incoming email."""
    apps = get_all_applications()
    if not apps:
        return None

    # Extract domain keyword from sender address (e.g. "google" from "recruiter@google.com")
    try:
        sender_domain = from_addr.split("@")[-1].split(".")[0].lower()
    except Exception:
        sender_domain = ""

    best_match = None
    best_score = 0.0

    for app in apps:
        score     = 0.0
        company   = (app.get("org") or "").lower()
        job_title = (app.get("title") or "").lower()
        subj_low  = subject.lower()

        # Domain match is the strongest signal
        if sender_domain and sender_domain in company:
            score += 0.40

        # Company name in subject
        if company and company in subj_low:
            score += 0.30

        # Job title keywords in subject
        for word in job_title.split():
            if len(word) > 3 and word in subj_low:
                score += 0.10

        if score > best_score:
            best_score = score
            best_match = app

    return best_match if best_score >= 0.30 else None


def find_linkedin_profile(sender_name: str, company: str) -> str:
    q = f"{sender_name} {company} LinkedIn".replace(" ", "%20")
    return f"https://www.linkedin.com/search/results/people/?keywords={q}"


def get_company_info(company: str) -> dict:
    prompt = f"""Provide brief company information for {company}.
Return ONLY this JSON:
{{
    "size": "<employee count estimate>",
    "industry": "<industry>",
    "known_for": "<1 sentence>",
    "interview_process": "<typical process>"
}}"""
    try:
        response = _get_llm().invoke([HumanMessage(content=prompt)])
        text     = re.sub(r'```json|```', '', response.content.strip()).strip()
        return json.loads(text)
    except Exception:
        return {"size": "Unknown", "industry": "Unknown", "known_for": "", "interview_process": ""}


def save_email_intel(data: dict, application_id: int = 0):
    conn = get_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO email_intel
            (application_id, email_from, email_subject, email_body, classification,
             sender_name, sender_linkedin, company_info)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            application_id or 0,
            data.get("from", ""), data.get("subject", ""),
            data.get("body", "")[:2000], data.get("classification", ""),
            data.get("sender_name", ""), data.get("sender_linkedin", ""),
            str(data.get("company_info", "")),
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        log.error(f"Save email intel error: {e}")


def run_email_agent(email_addr: str, password: str, provider: str = "gmail") -> list:
    log.info("Email Intelligence Agent starting...")
    mail = connect_email(email_addr, password, provider)
    if not mail:
        log.info("Could not connect to email")
        return []

    processed_ids = get_processed_message_ids()
    raw_emails    = fetch_recent_emails(mail, limit=30)
    results       = []

    for em in raw_emails:
        msg_id = em.get("message_id", "")

        # Skip already-processed messages
        if msg_id and msg_id in processed_ids:
            continue

        classification = classify_email(em)
        label          = classification.get("classification", "other")
        confidence     = float(classification.get("confidence", 0.0))

        if label == "other" and confidence < 0.4:
            continue

        company       = classification.get("company", "")
        sender_name   = classification.get("sender_name", "")
        linkedin_url  = find_linkedin_profile(sender_name, company)
        company_info  = get_company_info(company) if company else {}

        # Find matching application
        matched_app   = _find_matching_application(em["from"], em["subject"])
        application_id = matched_app["id"] if matched_app else 0

        # Update application status based on classification
        if matched_app and application_id:
            status_map = {
                "interview":  "interview",
                "offer":      "offer",
                "rejection":  "rejected",
            }
            new_status = status_map.get(label)
            if new_status:
                update_application_status(application_id, new_status)
                log.info(f"Updated application #{application_id} -> {new_status}")

        result = {
            **em,
            "classification":  label,
            "confidence":      confidence,
            "company":         company,
            "sender_name":     sender_name,
            "sender_linkedin": linkedin_url,
            "company_info":    company_info,
            "key_message":     classification.get("key_message", ""),
            "matched_app_id":  application_id,
        }

        save_email_intel(result, application_id)

        # Mark processed to avoid re-processing
        if msg_id:
            mark_message_processed(msg_id, label, confidence, em["subject"], em["from"])

        results.append(result)
        log.info(f"{label} [{confidence:.0%}]: {em['subject'][:60]}")

    log.info(f"Email Agent complete. {len(results)} job-related emails processed.")
    return results
