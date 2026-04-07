import sqlite3
import os
import pathlib
import datetime
import csv
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT     = pathlib.Path(__file__).parent.parent
DB_PATH  = str(ROOT / "artifacts" / "jobpilot.db")
CSV_PATH = str(ROOT / "artifacts" / "applications.csv")
EXCEL_DIR = str(ROOT / "artifacts")

os.makedirs(str(ROOT / "artifacts"), exist_ok=True)

# ── Database Setup ─────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT,
            org         TEXT,
            location    TEXT,
            url         TEXT,
            source      TEXT,
            fit_score   REAL DEFAULT 0,
            ats_score   REAL DEFAULT 0,
            salary_min  INTEGER DEFAULT 0,
            salary_max  INTEGER DEFAULT 0,
            freshness   INTEGER DEFAULT 5,
            status      TEXT DEFAULT 'new',
            posted_at   TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id          INTEGER,
            title           TEXT,
            org             TEXT,
            location        TEXT,
            url             TEXT,
            source          TEXT,
            fit_score       REAL,
            ats_score       REAL,
            salary_min      INTEGER,
            salary_max      INTEGER,
            status          TEXT DEFAULT 'applied',
            resume_path     TEXT,
            cover_path      TEXT,
            applied_at      TEXT DEFAULT CURRENT_TIMESTAMP,
            followup_date   TEXT,
            followup_done   INTEGER DEFAULT 0,
            notes           TEXT
        )
    """)
    con.commit()
    con.close()

def save_job(job: dict) -> int:
    init_db()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    salary = job.get("salary", {})
    cur.execute("""
        INSERT INTO jobs (title, org, location, url, source, fit_score, ats_score,
                          salary_min, salary_max, freshness, posted_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        job.get("title",""), job.get("org",""), job.get("location",""),
        job.get("url",""), job.get("source",""),
        job.get("fit_score", 0), job.get("ats_score", 0),
        salary.get("min", 0), salary.get("max", 0),
        job.get("freshness_score", 5), job.get("posted_at","")
    ))
    job_id = cur.lastrowid
    con.commit()
    con.close()
    return job_id

def log_application(job: dict, resume_path: str, cover_path: str, status: str = "applied") -> int:
    init_db()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    salary      = job.get("salary", {})
    applied_at  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    followup    = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")

    cur.execute("""
        INSERT INTO applications
        (title, org, location, url, source, fit_score, ats_score,
         salary_min, salary_max, status, resume_path, cover_path,
         applied_at, followup_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        job.get("title",""), job.get("org",""), job.get("location",""),
        job.get("url",""), job.get("source",""),
        job.get("fit_score",0), job.get("ats_score",0),
        salary.get("min",0), salary.get("max",0),
        status, resume_path, cover_path, applied_at, followup
    ))
    app_id = cur.lastrowid
    con.commit()
    con.close()

    # Also log to CSV
    log_to_csv(job, resume_path, cover_path, status, applied_at)
    print(f"   ✅ Logged: {job['title']} at {job['org']} — {status}")
    return app_id

def log_to_csv(job: dict, resume_path: str, cover_path: str, status: str, applied_at: str):
    newfile = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if newfile:
            w.writerow(["time","title","org","location","url","source",
                        "fit_score","status","resume","cover","followup_date"])
        followup = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        w.writerow([
            applied_at, job.get("title",""), job.get("org",""),
            job.get("location",""), job.get("url",""), job.get("source",""),
            job.get("fit_score",0), status,
            os.path.basename(resume_path), os.path.basename(cover_path), followup
        ])

def get_all_applications() -> list:
    init_db()
    con  = sqlite3.connect(DB_PATH)
    cur  = con.cursor()
    cur.execute("SELECT * FROM applications ORDER BY applied_at DESC")
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    con.close()
    return [dict(zip(cols, r)) for r in rows]

def update_status(app_id: int, status: str):
    init_db()
    con = sqlite3.connect(DB_PATH)
    con.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
    con.commit()
    con.close()

def get_stats() -> dict:
    init_db()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    total    = cur.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    applied  = cur.execute("SELECT COUNT(*) FROM applications WHERE status='applied'").fetchone()[0]
    skipped  = cur.execute("SELECT COUNT(*) FROM applications WHERE status='skipped'").fetchone()[0]
    interview= cur.execute("SELECT COUNT(*) FROM applications WHERE status='interview'").fetchone()[0]
    offer    = cur.execute("SELECT COUNT(*) FROM applications WHERE status='offer'").fetchone()[0]
    avg_fit  = cur.execute("SELECT AVG(fit_score) FROM applications WHERE status='applied'").fetchone()[0]
    con.close()
    return {
        "total":     total,
        "applied":   applied,
        "skipped":   skipped,
        "interview": interview,
        "offer":     offer,
        "avg_fit":   round(avg_fit or 0, 1)
    }

# ── Excel Report ───────────────────────────────────────
def generate_excel_report() -> str:
    apps  = get_all_applications()
    stats = get_stats()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    path  = os.path.join(EXCEL_DIR, f"job_report_{today}.xlsx")
    wb    = Workbook()

    DARK   = "1F4E79"
    MID    = "2E75B6"
    LIGHT  = "BDD7EE"
    WHITE  = "FFFFFF"
    GRAY   = "F2F2F2"
    GREEN  = "E2EFDA"
    ORANGE = "FCE4D6"
    RED    = "FFDFD7"

    def hfont(color=WHITE, size=10, bold=True):
        return Font(color=color, size=size, bold=bold, name="Calibri")

    def bfont(size=10, bold=False, color="000000"):
        return Font(size=size, bold=bold, name="Calibri", color=color)

    def fill(hex_color):
        return PatternFill("solid", fgColor=hex_color)

    def border():
        s = Side(style="thin", color="CCCCCC")
        return Border(left=s, right=s, top=s, bottom=s)

    def center():
        return Alignment(horizontal="center", vertical="center", wrap_text=True)

    def left():
        return Alignment(horizontal="left", vertical="center", wrap_text=True)

    # ── Sheet 1 — Summary ──────────────────────────────
    ws1 = wb.active
    ws1.title = "Summary"
    ws1.merge_cells("A1:F1")
    ws1["A1"] = "JobPilot AI - Daily Report"
    ws1["A1"].font      = Font(color=WHITE, size=16, bold=True, name="Calibri")
    ws1["A1"].fill      = fill(DARK)
    ws1["A1"].alignment = center()
    ws1.row_dimensions[1].height = 35

    ws1.merge_cells("A2:F2")
    ws1["A2"] = f"Generated: {datetime.datetime.now().strftime('%B %d, %Y %H:%M')}  |  Total: {stats['total']} applications"
    ws1["A2"].font      = Font(color=WHITE, size=10, name="Calibri")
    ws1["A2"].fill      = fill(MID)
    ws1["A2"].alignment = center()

    stat_data = [
        ["Total Applied", stats["applied"]],
        ["Skipped",       stats["skipped"]],
        ["Interviews",    stats["interview"]],
        ["Offers",        stats["offer"]],
        ["Avg Fit Score", f"{stats['avg_fit']}%"],
        ["Report Date",   today]
    ]
    for i, (label, value) in enumerate(stat_data, start=4):
        ws1[f"A{i}"] = label
        ws1[f"A{i}"].font   = bfont(10, True, DARK)
        ws1[f"A{i}"].fill   = fill(LIGHT)
        ws1[f"A{i}"].border = border()
        ws1[f"B{i}"] = str(value)
        ws1[f"B{i}"].font   = bfont(10)
        ws1[f"B{i}"].border = border()
    ws1.column_dimensions["A"].width = 25
    ws1.column_dimensions["B"].width = 30

    # ── Sheet 2 — Applications ─────────────────────────
    ws2 = wb.create_sheet("Applications")
    headers   = ["#","Date","Job Title","Company","Location","Source","Fit %","ATS %","Salary Range","Status","Follow-up","Resume","Cover Letter"]
    col_widths = [4,18,35,20,15,12,8,8,15,12,12,25,25]

    for col,(h,w) in enumerate(zip(headers,col_widths),1):
        cell           = ws2.cell(row=1, column=col, value=h)
        cell.font      = hfont()
        cell.fill      = fill(DARK)
        cell.alignment = center()
        cell.border    = border()
        ws2.column_dimensions[get_column_letter(col)].width = w
    ws2.row_dimensions[1].height = 22

    status_fills = {
        "applied":   GREEN,
        "skipped":   ORANGE,
        "interview": "FFF2CC",
        "offer":     "D9F2E6",
        "rejected":  RED
    }

    for i, app in enumerate(apps, start=2):
        salary_range = f"${app.get('salary_min',0)//1000}k-${app.get('salary_max',0)//1000}k"
        row_fill     = fill(GRAY) if i % 2 == 0 else fill(WHITE)
        data = [
            i-1,
            str(app.get("applied_at",""))[:16],
            app.get("title",""),
            app.get("org",""),
            app.get("location",""),
            app.get("source",""),
            app.get("fit_score",0),
            app.get("ats_score",0),
            salary_range,
            app.get("status",""),
            app.get("followup_date",""),
            os.path.basename(app.get("resume_path","")),
            os.path.basename(app.get("cover_path",""))
        ]
        for col, value in enumerate(data, 1):
            cell           = ws2.cell(row=i, column=col, value=value)
            cell.font      = bfont()
            cell.alignment = center() if col in [1,7,8,10] else left()
            cell.border    = border()
            if col == 10:
                status = str(value).lower()
                cell.fill = fill(status_fills.get(status, WHITE))
                cell.font = bfont(10, True)
            else:
                cell.fill = row_fill
        ws2.row_dimensions[i].height = 18

    ws2.freeze_panes = "A2"

    # ── Sheet 3 — Follow-ups ───────────────────────────
    ws3 = wb.create_sheet("Follow-ups")
    fu_headers = ["Job Title","Company","Applied","Follow-up Date","Done","Status","Notes"]
    fu_widths  = [35,20,15,15,8,12,35]
    for col,(h,w) in enumerate(zip(fu_headers,fu_widths),1):
        cell           = ws3.cell(row=1, column=col, value=h)
        cell.font      = hfont()
        cell.fill      = fill(MID)
        cell.alignment = center()
        cell.border    = border()
        ws3.column_dimensions[get_column_letter(col)].width = w

    pending = [a for a in apps if a.get("status") == "applied"]
    for i, app in enumerate(pending, start=2):
        row_fill = fill(GRAY) if i % 2 == 0 else fill(WHITE)
        data = [
            app.get("title",""), app.get("org",""),
            str(app.get("applied_at",""))[:10],
            app.get("followup_date",""),
            "No", app.get("status",""), ""
        ]
        for col, value in enumerate(data, 1):
            cell           = ws3.cell(row=i, column=col, value=value)
            cell.font      = bfont()
            cell.fill      = row_fill
            cell.border    = border()
            cell.alignment = left()
        ws3.row_dimensions[i].height = 18

    wb.save(path)
    print(f"✅ Excel report saved: {path}")
    return path

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized")
    path = generate_excel_report()
    print(f"✅ Report generated: {path}")