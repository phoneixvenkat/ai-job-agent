import mysql.connector
from mysql.connector import Error
import os
import os
from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST",     "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", "3306")),
    "user":     os.getenv("MYSQL_USER",     "root"),
    "password": os.getenv("MYSQL_PASSWORD", "jobpilot123"),
    "database": os.getenv("MYSQL_DATABASE", "jobpilot")
}


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"MySQL connection error: {e}")
        return None

def init_database():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS jobpilot")
        cursor.execute("USE jobpilot")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                title           VARCHAR(256),
                org             VARCHAR(256),
                location        VARCHAR(256),
                url             VARCHAR(512),
                source          VARCHAR(64),
                description     TEXT,
                fit_score       FLOAT DEFAULT 0,
                llm_score       FLOAT DEFAULT 0,
                ats_score       FLOAT DEFAULT 0,
                salary_min      INT DEFAULT 0,
                salary_max      INT DEFAULT 0,
                freshness_score INT DEFAULT 5,
                status          VARCHAR(32) DEFAULT 'new',
                posted_at       VARCHAR(128),
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_duplicate    BOOLEAN DEFAULT FALSE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                job_id          INT,
                title           VARCHAR(256),
                org             VARCHAR(256),
                location        VARCHAR(256),
                url             VARCHAR(512),
                source          VARCHAR(64),
                fit_score       FLOAT DEFAULT 0,
                llm_score       FLOAT DEFAULT 0,
                ats_score       FLOAT DEFAULT 0,
                salary_min      INT DEFAULT 0,
                salary_max      INT DEFAULT 0,
                status          VARCHAR(32) DEFAULT 'applied',
                resume_path     VARCHAR(512),
                cover_path      VARCHAR(512),
                applied_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                followup_date   DATE,
                followup_done   BOOLEAN DEFAULT FALSE,
                score_explanation TEXT,
                notes           TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_intel (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                application_id  INT,
                email_from      VARCHAR(256),
                email_subject   VARCHAR(512),
                email_body      TEXT,
                classification  VARCHAR(64),
                sender_name     VARCHAR(256),
                sender_linkedin VARCHAR(512),
                company_info    TEXT,
                detected_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adaptive_patterns (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                pattern_type    VARCHAR(64),
                pattern_value   VARCHAR(256),
                success_count   INT DEFAULT 0,
                total_count     INT DEFAULT 0,
                success_rate    FLOAT DEFAULT 0,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_gaps (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                skill_name      VARCHAR(128),
                frequency       INT DEFAULT 0,
                user_has        BOOLEAN DEFAULT FALSE,
                progress_pct    INT DEFAULT 0,
                resource        VARCHAR(512),
                week_date       DATE,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ MySQL database initialized successfully!")
        return True

    except Error as e:
        print(f"❌ Database init error: {e}")
        return False

def save_job(job: dict) -> int:
    conn = get_connection()
    if not conn: return -1
    try:
        cursor = conn.cursor()
        salary = job.get("salary", {})
        cursor.execute("""
            INSERT INTO jobs (title, org, location, url, source, description,
                            fit_score, llm_score, ats_score, salary_min, salary_max,
                            freshness_score, posted_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            job.get("title",""), job.get("org",""), job.get("location",""),
            job.get("url",""), job.get("source",""),
            job.get("description","")[:2000],
            job.get("fit_score",0), job.get("llm_score",0), job.get("ats_score",0),
            salary.get("min",0), salary.get("max",0),
            job.get("freshness_score",5), job.get("posted_at","")
        ))
        conn.commit()
        job_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return job_id
    except Error as e:
        print(f"Save job error: {e}")
        return -1

def log_application(job: dict, resume_path: str, cover_path: str,
                    status: str = "applied", explanation: str = "") -> int:
    conn = get_connection()
    if not conn: return -1
    try:
        import datetime
        cursor   = conn.cursor()
        salary   = job.get("salary", {})
        followup = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO applications
            (title, org, location, url, source, fit_score, llm_score, ats_score,
             salary_min, salary_max, status, resume_path, cover_path,
             followup_date, score_explanation)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            job.get("title",""), job.get("org",""), job.get("location",""),
            job.get("url",""), job.get("source",""),
            job.get("fit_score",0), job.get("llm_score",0), job.get("ats_score",0),
            salary.get("min",0), salary.get("max",0),
            status, resume_path, cover_path, followup, explanation
        ))
        conn.commit()
        app_id = cursor.lastrowid
        cursor.close()
        conn.close()
        print(f"✅ Logged: {job['title']} at {job['org']} — {status}")
        return app_id
    except Error as e:
        print(f"Log application error: {e}")
        return -1

def get_all_applications() -> list:
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM applications ORDER BY applied_at DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print(f"Get applications error: {e}")
        return []

def update_application_status(app_id: int, status: str):
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE applications SET status=%s WHERE id=%s", (status, app_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Update status error: {e}")

def get_stats() -> dict:
    conn = get_connection()
    if not conn: return {}
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM applications")
        total = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) as c FROM applications WHERE status='applied'")
        applied = cursor.fetchone()["c"]
        cursor.execute("SELECT COUNT(*) as c FROM applications WHERE status='interview'")
        interview = cursor.fetchone()["c"]
        cursor.execute("SELECT COUNT(*) as c FROM applications WHERE status='offer'")
        offer = cursor.fetchone()["c"]
        cursor.execute("SELECT COUNT(*) as c FROM applications WHERE status='rejected'")
        rejected = cursor.fetchone()["c"]
        cursor.execute("SELECT AVG(fit_score) as avg FROM applications WHERE status='applied'")
        avg_fit = cursor.fetchone()["avg"] or 0
        cursor.close()
        conn.close()
        return {
            "total":     total,
            "applied":   applied,
            "interview": interview,
            "offer":     offer,
            "rejected":  rejected,
            "avg_fit":   round(float(avg_fit), 1)
        }
    except Error as e:
        print(f"Get stats error: {e}")
        return {}

def check_duplicate(title: str, org: str) -> bool:
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM applications
            WHERE LOWER(title)=%s AND LOWER(org)=%s
        """, (title.lower(), org.lower()))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count > 0
    except Error as e:
        print(f"Check duplicate error: {e}")
        return False

def save_adaptive_pattern(pattern_type: str, pattern_value: str, success: bool):
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO adaptive_patterns (pattern_type, pattern_value, success_count, total_count)
            VALUES (%s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
                success_count = success_count + %s,
                total_count   = total_count + 1,
                success_rate  = (success_count + %s) / (total_count + 1)
        """, (pattern_type, pattern_value, 1 if success else 0,
              1 if success else 0, 1 if success else 0))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Save pattern error: {e}")

def get_adaptive_patterns() -> list:
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM adaptive_patterns
            WHERE total_count >= 3
            ORDER BY success_rate DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print(f"Get patterns error: {e}")
        return []

if __name__ == "__main__":
    init_database()