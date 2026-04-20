from database.mysql_db import get_connection
from mysql.connector import Error
import datetime

_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        from langchain_ollama import ChatOllama
        _llm = ChatOllama(model="llama3", base_url="http://localhost:11434", temperature=0.3)
    return _llm

def get_pending_followups() -> list:
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        today  = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT * FROM applications
            WHERE status = 'applied'
            AND followup_done = 0
            AND followup_date <= %s
            ORDER BY followup_date ASC
        """, (today,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print(f"Get followups error: {e}")
        return []

def generate_followup_email(app: dict) -> dict:
    prompt = f"""Write a professional follow-up email for a job application.

Job Title: {app.get('title')}
Company: {app.get('org')}
Applied: {str(app.get('applied_at',''))[:10]}
Days Since Applied: {(datetime.date.today() - datetime.date.fromisoformat(str(app.get('applied_at','2026-01-01'))[:10])).days}

Write a short, professional follow-up email:
- Subject line
- 3 short paragraphs
- Express continued interest
- Ask about timeline
- Professional closing

Return as:
SUBJECT: <subject>
BODY:
<body>"""

    try:
        from langchain_core.messages import HumanMessage
        response = _get_llm().invoke([HumanMessage(content=prompt)])
        text     = response.content.strip()
        lines    = text.split('\n')
        subject  = ""
        body     = ""
        in_body  = False
        for line in lines:
            if line.startswith("SUBJECT:"):
                subject = line.replace("SUBJECT:", "").strip()
            elif line.startswith("BODY:"):
                in_body = True
            elif in_body:
                body += line + "\n"
        return {
            "app_id":  app["id"],
            "title":   app["title"],
            "org":     app["org"],
            "subject": subject or f"Following Up — {app['title']} Application",
            "body":    body.strip() or f"Dear Hiring Team,\n\nI wanted to follow up on my application for the {app['title']} position at {app['org']}.\n\nBest regards,\nVenkatasaikumar Erla"
        }
    except Exception as e:
        return {
            "app_id":  app["id"],
            "title":   app["title"],
            "org":     app["org"],
            "subject": f"Following Up — {app['title']} Application",
            "body":    f"Dear Hiring Team,\n\nI wanted to follow up on my application for the {app['title']} position at {app['org']}.\n\nThank you for your time.\n\nBest regards,\nVenkatasaikumar Erla"
        }

def mark_followup_done(app_id: int):
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE applications SET followup_done=1 WHERE id=%s", (app_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Mark followup error: {e}")

def run_followup_agent() -> list:
    print("\n📧 Follow-up Agent starting...")
    pending  = get_pending_followups()
    print(f"   {len(pending)} follow-ups due today")
    drafts   = []
    for app in pending:
        print(f"   Drafting follow-up for {app['title']} at {app['org']}")
        draft = generate_followup_email(app)
        drafts.append(draft)
    print(f"✅ {len(drafts)} follow-up drafts generated")
    return drafts