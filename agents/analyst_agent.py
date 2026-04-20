import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from backend.utils.logger import get_logger
log = get_logger('analyst')


GROQ_API_KEY = "your_groq_api_key_here"
llm = ChatGroq(
    model="llama3-8b-8192",
    api_key=GROQ_API_KEY,
    temperature=0
)

load_dotenv()
llm = ChatGroq(model=os.getenv("GROQ_MODEL","llama-3.1-8b-instant"), api_key=os.getenv("GROQ_API_KEY"), temperature=0)

def calculate_fit_score(resume_text: str, job_description: str) -> float:
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
        matrix     = vectorizer.fit_transform([resume_text, job_description])
        score      = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(float(score) * 100, 1)
    except:
        return 0.0

def get_missing_skills(resume_text: str, job_description: str) -> list:
    tech_skills = [
        "python","r","sql","java","scala","spark","pyspark","hadoop","kafka",
        "airflow","dbt","mlflow","docker","kubernetes","aws","gcp","azure",
        "tensorflow","pytorch","scikit-learn","pandas","numpy","tableau",
        "powerbi","looker","snowflake","databricks","fastapi","flask","django",
        "langchain","langgraph","llm","rag","nlp","cv","deep learning",
        "machine learning","statistics","a/b testing","git","ci/cd"
    ]
    resume_lower = resume_text.lower()
    jd_lower     = job_description.lower()
    missing = []
    for skill in tech_skills:
        if skill in jd_lower and skill not in resume_lower:
            missing.append(skill)
    return missing[:8]

def calculate_ats_score(resume_text: str, job_description: str) -> dict:
    resume_lower = resume_text.lower()
    jd_lower     = job_description.lower()
    jd_words     = set(re.findall(r'\b\w{4,}\b', jd_lower))
    resume_words = set(re.findall(r'\b\w{4,}\b', resume_lower))
    stopwords    = {"that","this","with","have","from","they","will","your","about","been"}
    jd_keywords  = jd_words - stopwords
    matched      = jd_keywords & resume_words
    score        = round(len(matched) / max(len(jd_keywords), 1) * 100, 1)
    return {
        "score":           min(score, 100),
        "matched_keywords": len(matched),
        "total_keywords":  len(jd_keywords)
    }

def decode_jd(job_title: str, job_description: str) -> str:
    prompt = f"""You are an honest career advisor. Read this job description and decode the corporate language.
For each red flag phrase, explain what it REALLY means.
Keep it short — maximum 3 bullet points.
Format: "• [phrase] = [real meaning]"

Job: {job_title}
Description (first 800 chars): {job_description[:800]}

Give only the bullet points, no intro text."""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except:
        return "JD Decoder unavailable — Ollama not running"

def estimate_salary(job_title: str, location: str) -> dict:
    salary_map = {
        "data scientist":          {"min": 90000,  "max": 140000, "median": 115000},
        "machine learning engineer":{"min": 100000, "max": 160000, "median": 130000},
        "ai engineer":             {"min": 110000, "max": 170000, "median": 140000},
        "data analyst":            {"min": 65000,  "max": 110000, "median": 85000},
        "data engineer":           {"min": 95000,  "max": 150000, "median": 120000},
        "research scientist":      {"min": 100000, "max": 165000, "median": 135000},
        "software engineer":       {"min": 95000,  "max": 155000, "median": 125000},
        "ml engineer":             {"min": 100000, "max": 160000, "median": 130000},
    }
    title_lower = job_title.lower()
    for key, salary in salary_map.items():
        if key in title_lower:
            multiplier = 1.1 if "remote" in location.lower() else 1.0
            return {
                "min":    int(salary["min"] * multiplier),
                "max":    int(salary["max"] * multiplier),
                "median": int(salary["median"] * multiplier),
                "source": "Market estimate"
            }
    return {"min": 70000, "max": 130000, "median": 100000, "source": "General estimate"}

def analyze_job(job: dict, resume_text: str, decode: bool = False) -> dict:
    description = job.get("description", job.get("title", ""))
    fit_score   = calculate_fit_score(resume_text, description)
    missing     = get_missing_skills(resume_text, description)
    ats         = calculate_ats_score(resume_text, description)
    salary      = estimate_salary(job["title"], job.get("location", ""))
    jd_decoded  = decode_jd(job["title"], description) if decode else "Click to decode"

    job["fit_score"]      = fit_score
    job["missing_skills"] = missing
    job["ats_score"]      = ats["score"]
    job["salary"]         = salary
    job["jd_decoded"]     = jd_decoded

    return job

def run_analyst(jobs: list, resume_text: str, decode_jds: bool = False) -> list:
    log.info(f"\n Analyst Agent analyzing {len(jobs)} jobs...\n")
    analyzed = []
    for i, job in enumerate(jobs, 1):
        description = job.get("description", job.get("title", ""))
        fit_score   = calculate_fit_score(resume_text, description)
        missing     = get_missing_skills(resume_text, description)
        ats         = calculate_ats_score(resume_text, description)
        salary      = estimate_salary(job["title"], job.get("location", ""))

        job["fit_score"]      = fit_score
        job["missing_skills"] = missing
        job["ats_score"]      = ats["score"]
        job["salary"]         = salary
        job["jd_decoded"]     = "Click to decode"
        job["keywords"]       = missing[:6]

        analyzed.append(job)

    analyzed.sort(key=lambda x: x["fit_score"], reverse=True)
    log.info(f" Analysis complete. Top fit: {analyzed[0]['fit_score']}%\n")
    return analyzed