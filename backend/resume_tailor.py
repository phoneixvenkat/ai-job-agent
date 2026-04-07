from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

llm = ChatOllama(model="llama3", base_url="http://localhost:11434", temperature=0.3)

def tailor_resume(resume_text: str, job_title: str, job_description: str, company: str) -> str:
    prompt = f"""You are an expert resume writer. Rewrite the following resume to better match the job description.

Job Title: {job_title}
Company: {company}
Job Description (first 1000 chars): {job_description[:1000]}

Original Resume:
{resume_text}

Instructions:
- Keep all facts accurate, do not invent experience
- Reorder and emphasize skills that match the job
- Use keywords from the job description naturally
- Keep it under 400 words
- Return only the rewritten resume text, no extra commentary"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


def generate_cover_letter(resume_text: str, job_title: str, job_description: str, company: str) -> str:
    prompt = f"""Write a professional cover letter for this job application.

Job Title: {job_title}
Company: {company}
Job Description: {job_description[:800]}

Candidate Background:
{resume_text[:600]}

Instructions:
- 3 short paragraphs
- Professional but enthusiastic tone
- Mention 2-3 specific skills that match the role
- End with a call to action
- Return only the cover letter text"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()