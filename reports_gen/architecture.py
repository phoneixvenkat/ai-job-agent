import pathlib
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch, cm
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.graphics import renderPDF

ROOT = pathlib.Path(__file__).parent.parent

def generate_architecture_pdf():
    path = str(ROOT / "artifacts" / "JobPilot_AI_Architecture.pdf")
    doc  = SimpleDocTemplate(path, pagesize=landscape(A4), 
                              rightMargin=1*cm, leftMargin=1*cm,
                              topMargin=1*cm, bottomMargin=1*cm)
    
    styles = getSampleStyleSheet()
    story  = []

    title_style = ParagraphStyle('title', fontSize=24, fontName='Helvetica-Bold',
                                  textColor=colors.HexColor('#1E3A5F'), spaceAfter=6,
                                  alignment=1)
    sub_style   = ParagraphStyle('sub', fontSize=12, fontName='Helvetica',
                                  textColor=colors.HexColor('#4A6FA5'), spaceAfter=20,
                                  alignment=1)
    head_style  = ParagraphStyle('head', fontSize=11, fontName='Helvetica-Bold',
                                  textColor=colors.white, alignment=1)
    body_style  = ParagraphStyle('body', fontSize=9, fontName='Helvetica',
                                  textColor=colors.HexColor('#333333'), spaceAfter=4)
    agent_style = ParagraphStyle('agent', fontSize=10, fontName='Helvetica-Bold',
                                  textColor=colors.white, alignment=1, spaceAfter=2)
    feat_style  = ParagraphStyle('feat', fontSize=8, fontName='Helvetica',
                                  textColor=colors.HexColor('#E8F4FD'), alignment=1)

    story.append(Paragraph("JobPilot AI — Multi-Agent Architecture", title_style))
    story.append(Paragraph("AI-Powered Personal Career Agent | University of New Haven | MS Data Science Capstone 2026", sub_style))

    # ── Agent Table ────────────────────────────────────
    agent_colors = [
        colors.HexColor('#1565C0'),
        colors.HexColor('#00695C'),
        colors.HexColor('#6A1B9A'),
        colors.HexColor('#E65100'),
        colors.HexColor('#AD1457'),
        colors.HexColor('#37474F'),
    ]

    agents = [
        ["🔭 SCOUT AGENT", "🧪 ANALYST AGENT", "✍️ WRITER AGENT",
         "🤖 APPLIER AGENT", "📊 TRACKER AGENT", "📧 EMAIL AGENT"],
        [
            "• Greenhouse API\n• Lever API\n• LinkedIn Scraper\n• Remotive API\n• Indeed RSS\n• Wellfound API\n• Deduplication",
            "• TF-IDF Fit Score\n• LLM Matching\n• JD Decoder\n• ATS Score\n• Salary Intel\n• Culture Fit\n• Gap Analysis",
            "• Resume Tailoring\n• LLM Cover Letter\n• Bullet Selection\n• ATS Optimizer\n• Interview Prep\n• LinkedIn Message",
            "• Playwright Forms\n• Human Simulation\n• Form Detection\n• File Upload\n• Screenshot Proof\n• Submission Check",
            "• MySQL Logging\n• Excel Reports\n• Follow-up Drafts\n• Status Tracking\n• Adaptive Learning\n• Pattern Analysis",
            "• Gmail/Outlook\n• Email Classify\n• Interview Detect\n• Rejection Detect\n• LinkedIn Finder\n• Company Intel"
        ]
    ]

    col_w = [4.5*cm] * 6
    tbl   = Table(agents, colWidths=col_w, rowHeights=[1.2*cm, 5*cm])
    tbl_style = TableStyle([
        ('BACKGROUND',  (0,0), (0,0), agent_colors[0]),
        ('BACKGROUND',  (1,0), (1,0), agent_colors[1]),
        ('BACKGROUND',  (2,0), (2,0), agent_colors[2]),
        ('BACKGROUND',  (3,0), (3,0), agent_colors[3]),
        ('BACKGROUND',  (4,0), (4,0), agent_colors[4]),
        ('BACKGROUND',  (5,0), (5,0), agent_colors[5]),
        ('BACKGROUND',  (0,1), (0,1), colors.HexColor('#E3F2FD')),
        ('BACKGROUND',  (1,1), (1,1), colors.HexColor('#E0F2F1')),
        ('BACKGROUND',  (2,1), (2,1), colors.HexColor('#F3E5F5')),
        ('BACKGROUND',  (3,1), (3,1), colors.HexColor('#FFF3E0')),
        ('BACKGROUND',  (4,1), (4,1), colors.HexColor('#FCE4EC')),
        ('BACKGROUND',  (5,1), (5,1), colors.HexColor('#ECEFF1')),
        ('TEXTCOLOR',   (0,0), (5,0), colors.white),
        ('FONTNAME',    (0,0), (5,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (5,0), 11),
        ('FONTNAME',    (0,1), (5,1), 'Helvetica'),
        ('FONTSIZE',    (0,1), (5,1), 8),
        ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',        (0,0), (-1,-1), 1, colors.white),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [None, None]),
        ('TOPPADDING',  (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
    ])
    tbl.setStyle(tbl_style)
    story.append(tbl)
    story.append(Spacer(1, 0.3*cm))

    # ── Flow Table ─────────────────────────────────────
    flow_data = [[
        Paragraph("1️⃣ USER INPUT", head_style),
        Paragraph("→", head_style),
        Paragraph("2️⃣ JOB DISCOVERY", head_style),
        Paragraph("→", head_style),
        Paragraph("3️⃣ AI ANALYSIS", head_style),
        Paragraph("→", head_style),
        Paragraph("4️⃣ DOCUMENT GEN", head_style),
        Paragraph("→", head_style),
        Paragraph("5️⃣ REVIEW", head_style),
        Paragraph("→", head_style),
        Paragraph("6️⃣ SUBMIT", head_style),
        Paragraph("→", head_style),
        Paragraph("7️⃣ TRACK", head_style),
    ]]

    flow_details = [[
        Paragraph("Resume Upload\nTarget Roles\nCompanies\nSalary Min", feat_style),
        Paragraph("", feat_style),
        Paragraph("6 Platforms\nDedup Agents\n136+ Jobs\nFreshness Score", feat_style),
        Paragraph("", feat_style),
        Paragraph("Fit Score\nLLM Match\nATS Check\nSalary Intel", feat_style),
        Paragraph("", feat_style),
        Paragraph("Tailored Resume\nCover Letter\nInterview Prep\nATS Optimized", feat_style),
        Paragraph("", feat_style),
        Paragraph("Preview Docs\nQuality Score\nYES = Apply\nNO = Skip", feat_style),
        Paragraph("", feat_style),
        Paragraph("Playwright\nAuto-fill\nHuman Sim\nScreenshot", feat_style),
        Paragraph("", feat_style),
        Paragraph("MySQL Log\nExcel Report\nFollow-ups\nAdaptive AI", feat_style),
    ]]

    flow_cols = [3.2*cm, 0.5*cm, 3.2*cm, 0.5*cm, 3.2*cm, 0.5*cm,
                 3.2*cm, 0.5*cm, 3.2*cm, 0.5*cm, 3.2*cm, 0.5*cm, 3.2*cm]

    flow_tbl = Table(flow_data + flow_details, colWidths=flow_cols,
                     rowHeights=[0.8*cm, 2*cm])
    flow_style = TableStyle([
        ('BACKGROUND', (0,0),  (0,1),  colors.HexColor('#1565C0')),
        ('BACKGROUND', (2,0),  (2,1),  colors.HexColor('#00695C')),
        ('BACKGROUND', (4,0),  (4,1),  colors.HexColor('#6A1B9A')),
        ('BACKGROUND', (6,0),  (6,1),  colors.HexColor('#E65100')),
        ('BACKGROUND', (8,0),  (8,1),  colors.HexColor('#AD1457')),
        ('BACKGROUND', (10,0), (10,1), colors.HexColor('#37474F')),
        ('BACKGROUND', (12,0), (12,1), colors.HexColor('#1B5E20')),
        ('BACKGROUND', (1,0),  (1,1),  colors.HexColor('#F5F5F5')),
        ('BACKGROUND', (3,0),  (3,1),  colors.HexColor('#F5F5F5')),
        ('BACKGROUND', (5,0),  (5,1),  colors.HexColor('#F5F5F5')),
        ('BACKGROUND', (7,0),  (7,1),  colors.HexColor('#F5F5F5')),
        ('BACKGROUND', (9,0),  (9,1),  colors.HexColor('#F5F5F5')),
        ('BACKGROUND', (11,0), (11,1), colors.HexColor('#F5F5F5')),
        ('ALIGN',      (0,0),  (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0),  (-1,-1), 'MIDDLE'),
        ('GRID',       (0,0),  (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('TOPPADDING', (0,0),  (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ])
    flow_tbl.setStyle(flow_style)
    story.append(flow_tbl)
    story.append(Spacer(1, 0.3*cm))

    # ── Tech Stack ─────────────────────────────────────
    tech_data = [
        [Paragraph("<b>Layer</b>", body_style),
         Paragraph("<b>Technology</b>", body_style),
         Paragraph("<b>Purpose</b>", body_style),
         Paragraph("<b>Layer</b>", body_style),
         Paragraph("<b>Technology</b>", body_style),
         Paragraph("<b>Purpose</b>", body_style)],
        ["Agent Orchestration", "LangGraph", "Multi-agent coordination",
         "LLM", "Llama3 via Ollama", "Job matching & document generation"],
        ["Backend API", "FastAPI + Python", "15 REST endpoints",
         "Database", "MySQL 8.0", "Applications, patterns, email intel"],
        ["Frontend", "React + TypeScript", "8-page animated dashboard",
         "Job Sources", "6 Platforms", "Greenhouse, LinkedIn, Remotive+"],
        ["Resume Build", "python-docx", "Tailored DOCX generation",
         "Auto-Apply", "Playwright", "Human behavior simulation"],
        ["Fit Scoring", "TF-IDF + LLM", "Hybrid matching algorithm",
         "Reports", "openpyxl", "Professional Excel reports"],
    ]

    tech_tbl = Table(tech_data, colWidths=[3.5*cm, 3.5*cm, 5*cm, 3.5*cm, 3.5*cm, 5*cm])
    tech_style = TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  colors.HexColor('#1E3A5F')),
        ('TEXTCOLOR',     (0,0), (-1,0),  colors.white),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.HexColor('#F8F9FA'), colors.white]),
        ('GRID',          (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
    ])
    tech_tbl.setStyle(tech_style)
    story.append(tech_tbl)

    doc.build(story)
    print(f"✅ Architecture PDF saved: {path}")
    return path

if __name__ == "__main__":
    generate_architecture_pdf()