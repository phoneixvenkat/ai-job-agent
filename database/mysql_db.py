import mysql.connector
from mysql.connector import Error
import os
import datetime

DB_CONFIG = {
    "host":     os.environ.get("DB_HOST",     "localhost"),
    "port":     int(os.environ.get("DB_PORT", "3306")),
    "user":     os.environ.get("DB_USER",     "root"),
    "password": os.environ.get("DB_PASSWORD", "jobpilot123"),
    "database": os.environ.get("DB_NAME",     "jobpilot"),
}

def _serialize(row: dict) -> dict:
    """Convert non-JSON-serializable MySQL types to plain Python types."""
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
        print(f"MySQL connection error: {e}")
        return None

def init_database():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
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
                INDEX idx_source  (source),
                INDEX idx_status  (status),
                UNIQUE KEY uq_url (url(500))
            )
        """)

        # Add UNIQUE constraint on url for existing tables that predate this change
        try:
            cursor.execute("ALTER TABLE jobs ADD UNIQUE KEY uq_url (url(500))")
            conn.commit()
        except Error:
            pass  # already exists

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
                notes           TEXT,
                INDEX idx_status        (status),
                INDEX idx_followup_date (followup_date),
                INDEX idx_followup_done (followup_done),
                INDEX idx_applied_at    (applied_at)
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
                pattern_type    VARCHAR(64)  NOT NULL,
                pattern_value   VARCHAR(256) NOT NULL,
                success_count   INT DEFAULT 0,
                total_count     INT DEFAULT 0,
                success_rate    FLOAT DEFAULT 0,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uq_pattern (pattern_type, pattern_value)
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_log (
                id           INT AUTO_INCREMENT PRIMARY KEY,
                message_id   VARCHAR(512) NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_message_id (message_id(500))
            )
        """)

        # Add follow_up_needed column to applications if not yet present
        try:
            cursor.execute(
                "ALTER TABLE applications ADD COLUMN follow_up_needed TINYINT(1) DEFAULT 0"
            )
            conn.commit()
        except Error:
            pass  # column already exists

        conn.commit()
        cursor.close()
        conn.close()
        print("[OK] MySQL database initialized successfully!")
        return True

    except Error as e:
        print(f"[ERROR] Database init error: {e}")
        return False

def save_job(job: dict) -> int:
    conn = get_connection()
    if not conn:
        return -1
    try:
        cursor = conn.cursor()
        salary = job.get("salary", {})
        cursor.execute("""
            INSERT INTO jobs (title, org, location, url, source, description,
                            fit_score, llm_score, ats_score, salary_min, salary_max,
                            freshness_score, posted_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            job.get("title", ""), job.get("org", ""), job.get("location", ""),
            job.get("url", ""), job.get("source", ""),
            job.get("description", "")[:2000],
            job.get("fit_score", 0), job.get("llm_score", 0), job.get("ats_score", 0),
            salary.get("min", 0), salary.get("max", 0),
            job.get("freshness_score", 5), job.get("posted_at", ""),
        ))
        conn.commit()
        job_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return job_id
    except Error as e:
        print(f"Save job error: {e}")
        return -1

def save_jobs_to_db(jobs: list) -> tuple:
    """Bulk-insert jobs using url as unique key. Returns (saved, skipped)."""
    if not jobs:
        return 0, 0
    conn = get_connection()
    if not conn:
        return 0, 0
    saved = skipped = 0
    try:
        cursor = conn.cursor()
        for job in jobs:
            url = (job.get("url") or "").strip()
            if not url:
                skipped += 1
                continue
            salary = job.get("salary", {}) if isinstance(job.get("salary"), dict) else {}
            cursor.execute("""
                INSERT IGNORE INTO jobs
                    (title, org, location, url, source, description,
                     fit_score, llm_score, ats_score, salary_min, salary_max,
                     freshness_score, posted_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                job.get("title", ""), job.get("org", ""), job.get("location", ""),
                url, job.get("source", ""),
                (job.get("description", "") or "")[:2000],
                job.get("fit_score", 0), job.get("llm_score", 0), job.get("ats_score", 0),
                salary.get("min", 0), salary.get("max", 0),
                job.get("freshness_score", 5), job.get("posted_at", ""),
            ))
            if cursor.rowcount == 1:
                saved += 1
            else:
                skipped += 1
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"save_jobs_to_db error: {e}")
    return saved, skipped

def log_application(job: dict, resume_path: str, cover_path: str,
                    status: str = "applied", explanation: str = "") -> int:
    conn = get_connection()
    if not conn:
        return -1
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
            job.get("title", ""), job.get("org", ""), job.get("location", ""),
            job.get("url", ""), job.get("source", ""),
            job.get("fit_score", 0), job.get("llm_score", 0), job.get("ats_score", 0),
            salary.get("min", 0), salary.get("max", 0),
            status, resume_path, cover_path, followup, explanation,
        ))
        conn.commit()
        app_id = cursor.lastrowid
        cursor.close()
        conn.close()
        print(f"[OK] Logged: {job.get('title')} at {job.get('org')} - {status}")
        return app_id
    except Error as e:
        print(f"Log application error: {e}")
        return -1

def get_all_applications() -> list:
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
        print(f"Get applications error: {e}")
        return []

def update_application_status(app_id: int, status: str):
    conn = get_connection()
    if not conn:
        return
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
    if not conn:
        return {}
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
        cursor.execute("SELECT COUNT(*) as c FROM applications WHERE status='skipped'")
        skipped = cursor.fetchone()["c"]
        cursor.execute("SELECT AVG(fit_score) as avg FROM applications WHERE fit_score > 0")
        avg_fit = cursor.fetchone()["avg"] or 0
        cursor.close()
        conn.close()
        return {
            "total":     total,
            "applied":   applied,
            "interview": interview,
            "offer":     offer,
            "rejected":  rejected,
            "skipped":   skipped,
            "avg_fit":   round(float(avg_fit), 1),
        }
    except Error as e:
        print(f"Get stats error: {e}")
        return {}

def check_duplicate(title: str, org: str) -> bool:
    conn = get_connection()
    if not conn:
        return False
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
    if not conn:
        return
    try:
        inc = 1 if success else 0
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO adaptive_patterns (pattern_type, pattern_value, success_count, total_count, success_rate)
            VALUES (%s, %s, %s, 1, %s)
            ON DUPLICATE KEY UPDATE
                success_count = success_count + %s,
                total_count   = total_count + 1,
                success_rate  = (success_count + %s) / (total_count + 1)
        """, (pattern_type, pattern_value, inc, float(inc), inc, inc))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Save pattern error: {e}")

def get_adaptive_patterns() -> list:
    conn = get_connection()
    if not conn:
        return []
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
        return [_serialize(r) for r in rows]
    except Error as e:
        print(f"Get patterns error: {e}")
        return []

def get_applications_for_report() -> list:
    """Return applications joined with job URL for Excel export."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                a.id,
                a.title,
                a.org         AS company,
                a.location,
                a.url,
                a.source,
                a.fit_score   AS match_score,
                a.ats_score,
                a.status,
                a.applied_at,
                a.followup_date,
                a.followup_done,
                a.salary_min,
                a.salary_max,
                a.resume_path,
                a.cover_path,
                a.score_explanation
            FROM applications a
            ORDER BY a.applied_at DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [_serialize(r) for r in rows]
    except Error as e:
        print(f"get_applications_for_report error: {e}")
        return []


def get_processed_message_ids() -> set:
    """Load all already-processed email Message-IDs from DB."""
    conn = get_connection()
    if not conn:
        return set()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT message_id FROM email_log")
        ids = {row[0] for row in cursor.fetchall()}
        cursor.close()
        conn.close()
        return ids
    except Error as e:
        print(f"get_processed_message_ids error: {e}")
        return set()


def mark_message_processed(message_id: str):
    """Record a Message-ID so it is never re-processed."""
    if not message_id:
        return
    conn = get_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT IGNORE INTO email_log (message_id) VALUES (%s)", (message_id[:500],)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"mark_message_processed error: {e}")


def check_followups() -> int:
    """Flag applications with no response after 7 days. Returns number updated."""
    conn = get_connection()
    if not conn:
        return 0
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE applications
               SET follow_up_needed = 1
             WHERE status = 'applied'
               AND follow_up_needed = 0
               AND applied_at < DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        updated = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return updated
    except Error as e:
        print(f"check_followups error: {e}")
        return 0


if __name__ == "__main__":
    init_database()
