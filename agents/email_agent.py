import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import imaplib
import email
import re
from email.header import decode_header
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from database.mysql_db import get_connection, update_application_status
from mysql.connector import Error
import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

GROQ_API_KEY = "your_groq_api_key_here"
llm = ChatGroq(
    model="llama3-8b-8192",
    api_key=GROQ_API_KEY,
    temperature=0
)
load_dotenv()
llm = ChatGroq(model=os.getenv("GROQ_MODEL","llama-3.1-8b-instant"), api_key=os.getenv("GROQ_API_KEY"), temperature=0)

EMAIL_CONFIG = {
    "gmail": {
        "imap_server": "imap.gmail.com",
        "imap_port":   993
    },
    "outlook": {
        "imap_server": "outlook.office365.com",
        "imap_port":   993
    }
}

def connect_email(email_addr: str, password: str, provider: str = "gmail"):
    try:
        config = EMAIL_CONFIG[provider]
        mail   = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
        mail.login(email_addr, password)
        print(f"✅ Connected to {provider} inbox")
        return mail
    except Exception as e:
        print(f"❌ Email connection error: {e}")
        return None

def fetch_recent_emails(mail, limit: int = 20) -> list:
    try:
        mail.select("inbox")
        _, messages = mail.search(None, "ALL")
        email_ids   = messages[0].split()[-limit:]
        emails      = []

        for eid in reversed(email_ids):
            _, msg_data = mail.fetch(eid, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg     = email.message_from_bytes(response_part[1])
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()
                    sender  = msg.get("From", "")
                    body    = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                    emails.append({
                        "from":    sender,
                        "subject": subject,
                        "body":    body[:2000]
                    })
        return emails
    except Exception as e:
        print(f"Fetch emails error: {e}")
        return []

def classify_email(email_data: dict) -> dict:
    prompt = f"""Classify this email related to a job application.

From: {email_data['from']}
Subject: {email_data['subject']}
Body: {email_data['body'][:800]}

Classify as one of: INTERVIEW_INVITED, REJECTED, OFFER_RECEIVED, MORE_INFO_NEEDED, NOT_JOB_RELATED

Also extract:
- Company name
- Sender name
- Key message in 1 sentence

Return ONLY this JSON:
{{
    "classification": "<type>",
    "company": "<name>",
    "sender_name": "<name>",
    "key_message": "<1 sentence>"
}}"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        text     = response.content.strip()
        text     = re.sub(r'```json|```', '', text).strip()
        result   = json.loads(text)
        return result
    except:
        return {
            "classification": "NOT_JOB_RELATED",
            "company":        "",
            "sender_name":    "",
            "key_message":    ""
        }

def find_linkedin_profile(sender_name: str, company: str) -> str:
    search_query = f"{sender_name} {company} LinkedIn"
    return f"https://www.linkedin.com/search/results/people/?keywords={search_query.replace(' ', '%20')}"

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
        response = llm.invoke([HumanMessage(content=prompt)])
        text     = response.content.strip()
        text     = re.sub(r'```json|```', '', text).strip()
        return json.loads(text)
    except:
        return {"size": "Unknown", "industry": "Unknown", "known_for": "", "interview_process": ""}

def save_email_intel(data: dict):
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO email_intel
            (email_from, email_subject, email_body, classification,
             sender_name, sender_linkedin, company_info)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            data.get("from",""), data.get("subject",""),
            data.get("body","")[:2000], data.get("classification",""),
            data.get("sender_name",""), data.get("sender_linkedin",""),
            str(data.get("company_info",""))
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Save email intel error: {e}")

def run_email_agent(email_addr: str, password: str, provider: str = "gmail") -> list:
    print("\n📧 Email Intelligence Agent starting...\n")
    mail   = connect_email(email_addr, password, provider)
    if not mail:
        print("❌ Could not connect to email")
        return []

    emails  = fetch_recent_emails(mail, limit=30)
    results = []

    for em in emails:
        classification = classify_email(em)
        if classification["classification"] == "NOT_JOB_RELATED":
            continue

        company      = classification.get("company", "")
        sender_name  = classification.get("sender_name", "")
        linkedin_url = find_linkedin_profile(sender_name, company)
        company_info = get_company_info(company) if company else {}

        result = {
            **em,
            "classification": classification["classification"],
            "company":        company,
            "sender_name":    sender_name,
            "sender_linkedin": linkedin_url,
            "company_info":   company_info,
            "key_message":    classification.get("key_message","")
        }

        save_email_intel(result)
        results.append(result)

        print(f"📬 {classification['classification']}: {em['subject'][:50]}")
        print(f"   From: {sender_name} at {company}")
        print(f"   LinkedIn: {linkedin_url}\n")

    print(f"✅ Email Agent complete. {len(results)} job-related emails processed.\n")
    return results