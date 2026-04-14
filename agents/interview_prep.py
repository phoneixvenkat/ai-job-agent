from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from fpdf import FPDF
import pathlib
import datetime

llm  = ChatOllama(model="llama3", base_url="http://localhost:11434", temperature=0.3)
ROOT = pathlib.Path(__file__).parent.parent
OUT  = ROOT / "out"
OUT.mkdir(exist_ok=True)

def generate_interview_prep(job: dict, resume_text: str) -> dict:
    prompt = f"""Create a comprehensive interview preparation guide.

Job: {job.get('title')} at {job.get('org')}
Description: {job.get('description', job.get('title',''))[:1000]}
Candidate Background: {resume_text[:500]}

Generate:
## TECHNICAL QUESTIONS (5 questions with suggested answers)
## BEHAVIORAL QUESTIONS (3 questions with STAR method answers)
## QUESTIONS TO ASK INTERVIEWER (3 smart questions)
## COMPANY RESEARCH POINTS (4 key things to know)
## KEY SKILLS TO HIGHLIGHT (top 5 from your background)

Be specific and actionable."""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content  = response.content.strip()
    except:
        content = f"""## TECHNICAL QUESTIONS
1. Describe your experience with machine learning pipelines.
2. How have you used Python for data analysis?
3. Explain a challenging ML project you worked on.
4. How do you handle imbalanced datasets?
5. Describe your experience with NLP.

## BEHAVIORAL QUESTIONS
1. Tell me about a time you solved a complex problem.
2. Describe a project where you had to learn quickly.
3. How do you handle disagreements with teammates?

## QUESTIONS TO ASK
1. What does success look like in this role after 90 days?
2. What are the biggest challenges the team is facing?
3. How is the team structured?

## COMPANY RESEARCH
1. Review {job.get('org')} recent news and products
2. Check Glassdoor reviews
3. Research their tech stack
4. Look up the interviewer on LinkedIn"""

    # Save as PDF
    ts   = int(datetime.datetime.now().timestamp())
    path = str(OUT / f"interview_prep_{job.get('org','company')}_{ts}.pdf")

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"Interview Prep: {job.get('title')} at {job.get('org')}", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, f"Generated: {datetime.datetime.now().strftime('%B %d, %Y')}", ln=True)
        pdf.ln(5)
        pdf.set_font("Helvetica", "", 10)
        for line in content.split('\n'):
            if line.startswith('##'):
                pdf.set_font("Helvetica", "B", 12)
                pdf.ln(3)
                pdf.cell(0, 8, line.replace('##','').strip(), ln=True)
                pdf.set_font("Helvetica", "", 10)
            else:
                pdf.multi_cell(0, 6, line)
        pdf.output(path)
    except Exception as e:
        print(f"PDF generation error: {e}")
        path = ""

    return {
        "job":     job,
        "content": content,
        "pdf_path": path
    }