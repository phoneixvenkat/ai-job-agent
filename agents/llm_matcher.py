import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

GROQ_API_KEY = "your_groq_api_key_here"
llm = ChatGroq(
    model="llama3-8b-8192",
    api_key=GROQ_API_KEY,
    temperature=0
)
import json
import re

load_dotenv()
llm = ChatGroq(model=os.getenv("GROQ_MODEL","llama-3.1-8b-instant"), api_key=os.getenv("GROQ_API_KEY"), temperature=0)

def llm_match_job(resume_text: str, job: dict) -> dict:
    title       = job.get("title", "")
    org         = job.get("org", "")
    description = job.get("description", job.get("title", ""))[:1500]

    prompt = f"""You are an expert career advisor and job matching specialist.
Analyze how well this candidate matches the job and provide a detailed assessment.

JOB DETAILS:
Title: {title}
Company: {org}
Description: {description}

CANDIDATE RESUME:
{resume_text[:1000]}

Provide your analysis in this EXACT JSON format:
{{
    "llm_score": <number 0-100>,
    "recommendation": "<APPLY|SKIP|CONSIDER>",
    "match_reason": "<2 sentences why they match or don't>",
    "missing_skills": ["skill1", "skill2"],
    "strong_matches": ["skill1", "skill2"],
    "apply_decision": "<Yes/No and one sentence why>"
}}

Return ONLY the JSON, no other text."""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        text     = response.content.strip()
        text     = re.sub(r'```json|```', '', text).strip()
        result   = json.loads(text)
        return {
            "llm_score":     float(result.get("llm_score", 50)),
            "recommendation": result.get("recommendation", "CONSIDER"),
            "match_reason":  result.get("match_reason", ""),
            "missing_skills": result.get("missing_skills", []),
            "strong_matches": result.get("strong_matches", []),
            "apply_decision": result.get("apply_decision", "")
        }
    except Exception as e:
        print(f"LLM matcher error: {e}")
        return {
            "llm_score":     50.0,
            "recommendation": "CONSIDER",
            "match_reason":  "LLM analysis unavailable",
            "missing_skills": [],
            "strong_matches": [],
            "apply_decision": "Manual review needed"
        }

def batch_match(resume_text: str, jobs: list) -> list:
    print(f"\n🧠 LLM Matcher analyzing {len(jobs)} jobs...\n")
    for i, job in enumerate(jobs, 1):
        print(f"  [{i}/{len(jobs)}] Matching: {job['title']} at {job['org']}")
        result = llm_match_job(resume_text, job)
        job["llm_score"]      = result["llm_score"]
        job["recommendation"] = result["recommendation"]
        job["match_reason"]   = result["match_reason"]
        job["missing_skills"] = result.get("missing_skills", [])
        job["strong_matches"] = result.get("strong_matches", [])
        job["apply_decision"] = result["apply_decision"]
        print(f"     Score: {result['llm_score']}% | {result['recommendation']} | {result['apply_decision'][:50]}")
    jobs.sort(key=lambda x: x["llm_score"], reverse=True)
    print(f"\n✅ LLM matching complete!\n")
    return jobs