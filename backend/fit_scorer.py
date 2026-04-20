from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text.strip()

def calculate_fit_score(resume_text: str, job_description: str) -> float:
    try:
        resume_clean = clean_text(resume_text)
        jd_clean     = clean_text(job_description)
        vectorizer   = TfidfVectorizer(stop_words="english", max_features=500)
        matrix       = vectorizer.fit_transform([resume_clean, jd_clean])
        score        = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(float(score) * 100, 1)
    except Exception:
        return 0.0

def get_matching_keywords(resume_text: str, job_description: str) -> list:
    try:
        resume_words = set(clean_text(resume_text).split())
        jd_words     = set(clean_text(job_description).split())
        stopwords    = {"the","and","for","with","you","are","that","this","have","will","from","our","your","we","be","to","of","in","a","an","is","it","as","at","by","or","on","not","but","was","has","had","do","can","would","should","could","may","might","must"}
        matches      = (resume_words & jd_words) - stopwords
        return sorted([w for w in matches if len(w) > 3])[:15]
    except Exception:
        return []