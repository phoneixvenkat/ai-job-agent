import os
import pathlib
import datetime
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from database.mysql_db import get_applications_for_report, get_stats
from backend.utils.logger import get_logger

log      = get_logger("tracker")
ROOT     = pathlib.Path(__file__).parent.parent
EXCEL_DIR = str(ROOT / "reports")
os.makedirs(EXCEL_DIR, exist_ok=True)

# ── Style helpers ──────────────────────────────────────
DARK, MID, LIGHT = "1F4E79", "2E75B6", "BDD7EE"
WHITE, GRAY      = "FFFFFF", "F2F2F2"
GREEN, ORANGE, RED = "E2EFDA", "FCE4D6", "FFDFD7"

def _font(color=WHITE, size=10, bold=True):
    return Font(color=color, size=size, bold=bold, name="Calibri")

def _fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def _border():
    s = Side(style="thin", color="CCCCCC")
    return Border(left=s, right=s, top=s, bottom=s)

def _center():
    return Alignment(horizontal="center", vertical="center", wrap_text=True)

def _left():
    return Alignment(horizontal="left", vertical="center", wrap_text=True)

STATUS_FILLS = {
    "applied":   GREEN,
    "interview": "FFF2CC",
    "offer":     "D9F2E6",
    "rejected":  RED,
    "skipped":   ORANGE,
}


def _header_row(ws, headers, widths, fill_color=DARK):
    for col, (h, w) in enumerate(zip(headers, widths), 1):
        cell           = ws.cell(row=1, column=col, value=h)
        cell.font      = _font()
        cell.fill      = _fill(fill_color)
        cell.alignment = _center()
        cell.border    = _border()
        ws.column_dimensions[get_column_letter(col)].width = w
    ws.row_dimensions[1].height = 22


def generate_excel_report() -> str:
    apps  = get_applications_for_report()
    stats = get_stats()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    path  = os.path.join(EXCEL_DIR, f"job_report_{today}.xlsx")
    wb    = Workbook()

    # ── Sheet 1 — Quick View (required columns) ────────
    ws1 = wb.active
    ws1.title = "Quick View"

    _header_row(ws1,
        ["#", "Job Title", "Company", "Match Score", "Status", "Applied Date", "URL"],
        [4,    35,          22,         13,            12,       16,             45],
    )

    for i, app in enumerate(apps, start=2):
        score    = app.get("match_score") or 0
        status   = str(app.get("status", "")).lower()
        row_fill = _fill(GRAY) if i % 2 == 0 else _fill(WHITE)
        data = [
            i - 1,
            app.get("title",       "") or "",
            app.get("company",     "") or "",
            round(float(score), 1),
            status,
            str(app.get("applied_at", "") or "")[:10],
            app.get("url",         "") or "",
        ]
        for col, value in enumerate(data, 1):
            cell           = ws1.cell(row=i, column=col, value=value)
            cell.font      = _font("000000", 10, col == 5)
            cell.border    = _border()
            cell.alignment = _center() if col in (1, 4) else _left()
            if col == 5:
                cell.fill = _fill(STATUS_FILLS.get(status, WHITE))
            else:
                cell.fill = row_fill
        ws1.row_dimensions[i].height = 18

    ws1.freeze_panes = "A2"

    # ── Sheet 2 — Full Detail ──────────────────────────
    ws2 = wb.create_sheet("Full Detail")
    _header_row(ws2,
        ["#","Applied","Title","Company","Location","Source","Fit%","ATS%","Salary","Status","Follow-up","Resume","Cover"],
        [4,   16,       35,     22,        15,       12,      8,     8,     14,     12,      12,         24,      24],
    )

    for i, app in enumerate(apps, start=2):
        sal = f"${int(app.get('salary_min') or 0)//1000}k–${int(app.get('salary_max') or 0)//1000}k"
        row_fill = _fill(GRAY) if i % 2 == 0 else _fill(WHITE)
        status   = str(app.get("status", "")).lower()
        data = [
            i - 1,
            str(app.get("applied_at", "") or "")[:16],
            app.get("title",    "") or "",
            app.get("company",  "") or "",
            app.get("location", "") or "",
            app.get("source",   "") or "",
            round(float(app.get("match_score") or 0), 1),
            round(float(app.get("ats_score")   or 0), 1),
            sal,
            status,
            str(app.get("followup_date", "") or "")[:10],
            os.path.basename(str(app.get("resume_path", "") or "")),
            os.path.basename(str(app.get("cover_path",  "") or "")),
        ]
        for col, value in enumerate(data, 1):
            cell           = ws2.cell(row=i, column=col, value=value)
            cell.font      = _font("000000", 10, col == 10)
            cell.border    = _border()
            cell.alignment = _center() if col in (1, 7, 8, 10) else _left()
            if col == 10:
                cell.fill = _fill(STATUS_FILLS.get(status, WHITE))
            else:
                cell.fill = row_fill
        ws2.row_dimensions[i].height = 18

    ws2.freeze_panes = "A2"

    # ── Sheet 3 — Summary Stats ────────────────────────
    ws3 = wb.create_sheet("Summary")
    ws3.merge_cells("A1:C1")
    ws3["A1"] = f"JobPilot AI Report — {datetime.datetime.now().strftime('%B %d, %Y %H:%M')}"
    ws3["A1"].font      = _font(size=14)
    ws3["A1"].fill      = _fill(DARK)
    ws3["A1"].alignment = _center()
    ws3.row_dimensions[1].height = 30

    for i, (label, value) in enumerate([
        ("Total Applications", stats.get("total",     0)),
        ("Applied",            stats.get("applied",   0)),
        ("Interviews",         stats.get("interview", 0)),
        ("Offers",             stats.get("offer",     0)),
        ("Rejected",           stats.get("rejected",  0)),
        ("Skipped",            stats.get("skipped",   0)),
        ("Avg Match Score",    f"{stats.get('avg_fit', 0)}%"),
    ], start=3):
        ws3[f"A{i}"] = label
        ws3[f"A{i}"].font   = _font(DARK, bold=True)
        ws3[f"A{i}"].fill   = _fill(LIGHT)
        ws3[f"A{i}"].border = _border()
        ws3[f"B{i}"] = str(value)
        ws3[f"B{i}"].font   = _font("000000", bold=False)
        ws3[f"B{i}"].border = _border()

    ws3.column_dimensions["A"].width = 25
    ws3.column_dimensions["B"].width = 20

    wb.save(path)
    log.info("Excel report saved: %s (%d rows)", path, len(apps))
    return path
