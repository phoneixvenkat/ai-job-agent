from database.mysql_db import update_application_status
from intelligence.adaptive_pattern import learn_from_application

_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        from langchain_ollama import ChatOllama
        _llm = ChatOllama(model="llama3", base_url="http://localhost:11434", temperature=0)
    return _llm

def handle_rejection(app_id: int, job: dict, resume_text: str) -> dict:
    print(f"\n💔 Rejection Handler: {job.get('title')} at {job.get('org')}")
    update_application_status(app_id, "rejected")
    learn_from_application(job, "rejected")

    prompt = f"""A job application was rejected. Provide honest actionable feedback.

Job: {job.get('title')} at {job.get('org')}
Fit Score: {job.get('fit_score', 0)}%
Missing Skills: {', '.join(job.get('missing_skills', []))}

Provide:
1. Most likely reason for rejection (1 sentence)
2. Top 3 specific improvements to make
3. 2 similar job titles to target instead

Be direct and constructive."""

    try:
        from langchain_core.messages import HumanMessage
        response = _get_llm().invoke([HumanMessage(content=prompt)])
        analysis = response.content.strip()
    except Exception:
        analysis = "Focus on the missing skills identified in your fit score analysis."

    return {
        "status":   "rejected",
        "job":      job,
        "analysis": analysis,
        "action":   "Review skill gaps and apply to similar roles"
    }

def handle_acceptance(app_id: int, job: dict) -> dict:
    print(f"\n🎉 Acceptance Handler: {job.get('title')} at {job.get('org')}")
    update_application_status(app_id, "interview")
    learn_from_application(job, "interview")

    prompt = f"""Prepare interview preparation for this role.

Job: {job.get('title')} at {job.get('org')}
Description: {job.get('description', '')[:800]}

Generate:
1. Top 5 likely technical interview questions
2. Top 3 behavioral questions
3. 2 smart questions to ask the interviewer
4. Key things to research about the company

Format as plain text with clear sections."""

    try:
        from langchain_core.messages import HumanMessage
        response = _get_llm().invoke([HumanMessage(content=prompt)])
        prep     = response.content.strip()
    except Exception:
        prep = f"Research {job.get('org')} thoroughly and prepare examples of your ML/DS projects."

    return {
        "status":   "interview",
        "job":      job,
        "prep_kit": prep,
        "action":   "Schedule interview and review prep kit"
    }

def handle_offer(app_id: int, job: dict) -> dict:
    print(f"\n🏆 Offer Handler: {job.get('title')} at {job.get('org')}")
    update_application_status(app_id, "offer")
    learn_from_application(job, "offer")
    return {
        "status": "offer",
        "job":    job,
        "action": "Review offer details and negotiate if needed"
    }

def handle_need_more_info(app_id: int, job: dict) -> dict:
    print(f"\n❓ More Info Handler: {job.get('title')} at {job.get('org')}")

    prompt = f"""This job needs more information before applying.

Job: {job.get('title')} at {job.get('org')}
Description: {job.get('description', '')[:500]}

What key information is missing? List 3 specific questions to research."""

    try:
        from langchain_core.messages import HumanMessage
        response  = _get_llm().invoke([HumanMessage(content=prompt)])
        questions = response.content.strip()
    except Exception:
        questions = "Research salary range, team size, and tech stack before applying."

    return {
        "status":    "need_info",
        "job":       job,
        "questions": questions,
        "action":    "Research these questions before deciding to apply"
    }