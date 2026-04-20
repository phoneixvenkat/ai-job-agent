_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        from langchain_ollama import ChatOllama
        _llm = ChatOllama(model="llama3", base_url="http://localhost:11434", temperature=0)
    return _llm

def explain_application_score(job: dict, resume_text: str) -> dict:
    fit_score = job.get("fit_score", 0)
    llm_score = job.get("llm_score", 0)
    combined  = round((fit_score * 0.4) + (llm_score * 0.6), 1)

    if combined >= 75:
        recommendation = "APPLY"
        color          = "green"
    elif combined >= 50:
        recommendation = "CONSIDER"
        color          = "yellow"
    else:
        recommendation = "SKIP"
        color          = "red"

    prompt = f"""You are a career advisor. Explain this job application score in plain English.
Be direct and honest. Maximum 3 sentences.

Job: {job.get('title')} at {job.get('org')}
Combined Score: {combined}%
TF-IDF Score: {fit_score}%
LLM Score: {llm_score}%
Missing Skills: {', '.join(job.get('missing_skills', [])[:3])}
Strong Matches: {', '.join(job.get('strong_matches', [])[:3])}
Recommendation: {recommendation}

Explain WHY the score is {combined}% and whether they should apply.
Return only the explanation, no headers."""

    try:
        from langchain_core.messages import HumanMessage
        response    = _get_llm().invoke([HumanMessage(content=prompt)])
        explanation = response.content.strip()
    except Exception:
        explanation = f"Combined score of {combined}% based on skill matching and job requirements analysis."

    return {
        "combined_score":  combined,
        "fit_score":       fit_score,
        "llm_score":       llm_score,
        "recommendation":  recommendation,
        "color":           color,
        "explanation":     explanation,
        "should_apply":    recommendation != "SKIP"
    }