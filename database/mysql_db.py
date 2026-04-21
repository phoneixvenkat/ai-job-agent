import mysql.connector
from mysql.connector import Error
import os
import datetime
from dotenv import load_dotenv
from backend.utils.logger import get_logger
log = get_logger('mysql')

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST",     "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", "3306")),
    "user":     os.getenv("MYSQL_USER",     "root"),
    "password": os.getenv("MYSQL_PASSWORD", "jobpilot123"),
    "database": os.getenv("MYSQL_DATABASE", "jobpilot")
}


def _serialize(row: dict) -> dict:
    result = {}
    for k, v in row.items():
        if isinstance(v, (datetime.datetime, datetime.date)):
            result[k] = str(v)
        elif isinstance(v, bytes):
            result[k] = v.decode("utf-8", errors="ignore")
        else:
            result[k] = v
    return result


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        log.error(f"MySQL connection error: {e}")
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
                is_duplicate    BOOLEAN DEFAULT FALSE,
                UNIQUE KEY uq_url (url(500))
            )
        """)

        # Safe ALTER for existing tables without UNIQUE KEY
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.statistics
            WHERE table_schema='jobpilot' AND table_name='jobs' AND index_name='uq_url'
        """)
        if cursor.fetchone()[0] == 0:
            try:
                cursor.execute("ALTER TABLE jobs ADD UNIQUE KEY uq_url (url(500))")
            except Error:
                pass

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
                follow_up_needed TINYINT(1) DEFAULT 0,
                score_explanation TEXT,
                notes           TEXT
            )
        """)

        # Safe ALTER for follow_up_needed on existing tables
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema='jobpilot' AND table_name='applications' AND column_name='follow_up_needed'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE applications ADD COLUMN follow_up_needed TINYINT(1) DEFAULT 0")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_log (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                message_id      VARCHAR(256) UNIQUE,
                application_id  INT,
                email_from      VARCHAR(256),
                email_subject   VARCHAR(512),
                email_body      TEXT,
                classification  VARCHAR(64),
                confidence      FLOAT DEFAULT 0,
                sender_name     VARCHAR(256),
                sender_linkedin VARCHAR(512),
                company_info    TEXT,
                detected_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_log (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                agent_name  VARCHAR(64),
                status      VARCHAR(32),
                message     TEXT,
                result_json TEXT,
                started_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finished_at TIMESTAMP NULL
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
        log.info("[OK] MySQL database initialized successfully!")
        return True

    except Error as e:
        log.error(f"[ERROR] Database init error: {e}")
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
        log.error(f"Save job error: {e}")
        return -1


def save_jobs_to_db(jobs: list) -> tuple:
    """Bulk-insert jobs using INSERT IGNORE to skip URL duplicates. Returns (saved, skipped)."""
    conn = get_connection()
    if not conn:
        return 0, len(jobs)
    saved = 0
    skipped = 0
    try:
        cursor = conn.cursor()
        for job in jobs:
            salary = job.get("salary", {})
            try:
                cursor.execute("""
                    INSERT IGNORE INTO jobs
                        (title, org, location, url, source, description,
                         fit_score, llm_score, ats_score, salary_min, salary_max,
                         freshness_score, posted_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    job.get("title",""), job.get("org",""), job.get("location",""),
                    job.get("url",""), job.get("source",""),
                    str(job.get("description",""))[:2000],
                    job.get("fit_score",0), job.get("llm_score",0), job.get("ats_score",0),
                    salary.get("min",0) if isinstance(salary, dict) else 0,
                    salary.get("max",0) if isinstance(salary, dict) else 0,
                    job.get("freshness_score",5), job.get("posted_at","")
                ))
                if cursor.rowcount > 0:
                    saved += 1
                else:
                    skipped += 1
            except Error:
                skipped += 1
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        log.error(f"save_jobs_to_db error: {e}")
    return saved, skipped


def log_application(job: dict, resume_path: str, cover_path: str,
                    status: str = "applied", explanation: str = "") -> int:
    conn = get_connection()
    if not conn: return -1
    try:
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
            salary.get("min",0) if isinstance(salary, dict) else 0,
            salary.get("max",0) if isinstance(salary, dict) else 0,
            status, resume_path, cover_path, followup, explanation
        ))
        conn.commit()
        app_id = cursor.lastrowid
        cursor.close()
        conn.close()
        log.info(f"[OK] Logged: {job.get('title','')} at {job.get('org','')} - {status}")
        return app_id
    except Error as e:
        log.error(f"Log application error: {e}")
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
        return [_serialize(r) for r in rows]
    except Error as e:
        log.error(f"Get applications error: {e}")
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
        log.error(f"Update status error: {e}")

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
        log.error(f"Get stats error: {e}")
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
        log.error(f"Check duplicate error: {e}")
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
        log.error(f"Save pattern error: {e}")

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
        log.error(f"Get patterns error: {e}")
        return []

def get_jobs_count() -> int:
    conn = get_connection()
    if not conn:
        return 0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM jobs")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Error as e:
        log.error(f"get_jobs_count error: {e}")
        return 0


def get_all_jobs(limit: int = 50, offset: int = 0) -> tuple:
    """Return (jobs_list, total_count) from jobs table."""
    conn = get_connection()
    if not conn:
        return [], 0
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as c FROM jobs")
        total = cursor.fetchone()["c"]
        cursor.execute("""
            SELECT id, title, org AS company, location, source, url,
                   fit_score AS match_score, status, created_at,
                   description
            FROM jobs
            ORDER BY fit_score DESC, created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [_serialize(r) for r in rows], total
    except Error as e:
        log.error(f"get_all_jobs error: {e}")
        return [], 0


def get_applications_for_report() -> list:
    """Return all applications with all columns for Excel report generation."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM applications ORDER BY applied_at DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [_serialize(r) for r in rows]
    except Error as e:
        log.error(f"get_applications_for_report error: {e}")
        return []


def get_followup_applications() -> list:
    """Return applications flagged for follow-up."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM applications
            WHERE follow_up_needed = 1
            ORDER BY applied_at ASC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [_serialize(r) for r in rows]
    except Error as e:
        log.error(f"get_followup_applications error: {e}")
        return []


def check_followups() -> int:
    """Flag applications with no response after 7 days. Returns count flagged."""
    conn = get_connection()
    if not conn:
        return 0
    try:
        cursor = conn.cursor()
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE applications
            SET follow_up_needed = 1
            WHERE status = 'applied'
              AND applied_at <= %s
              AND follow_up_needed = 0
        """, (cutoff,))
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        if count:
            log.info(f"[OK] Flagged {count} applications for follow-up")
        return count
    except Error as e:
        log.error(f"check_followups error: {e}")
        return 0


def get_processed_message_ids() -> set:
    """Return set of already-processed email message IDs."""
    conn = get_connection()
    if not conn:
        return set()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT message_id FROM email_log WHERE message_id IS NOT NULL")
        ids = {row[0] for row in cursor.fetchall()}
        cursor.close()
        conn.close()
        return ids
    except Error as e:
        log.error(f"get_processed_message_ids error: {e}")
        return set()


def mark_message_processed(message_id: str, classification: str,
                            confidence: float, subject: str, from_addr: str):
    """Insert a processed email record to prevent re-processing."""
    conn = get_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT IGNORE INTO email_log
                (message_id, classification, confidence, email_subject, email_from)
            VALUES (%s, %s, %s, %s, %s)
        """, (message_id, classification, confidence, subject, from_addr))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        log.error(f"mark_message_processed error: {e}")


if __name__ == "__main__":
    init_database()
