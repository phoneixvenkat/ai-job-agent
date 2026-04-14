# 🧠 JobPilot AI — Matching Algorithm Documentation

## Overview

JobPilot AI uses a **hybrid matching system** combining traditional NLP (TF-IDF) with Large Language Model (LLM) intelligence to score job fit.

---

## Algorithm 1 — TF-IDF Fit Scorer

### What is TF-IDF?
TF-IDF (Term Frequency-Inverse Document Frequency) measures how relevant words in a document are compared to a collection of documents.

### How We Use It

```python
# Both resume and job description become TF-IDF vectors
vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
matrix     = vectorizer.fit_transform([resume_text, job_description])

# Cosine similarity measures angle between vectors
# 0 = completely different, 1 = identical
fit_score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100
```

### Why TF-IDF?
- Fast — processes 20 jobs in under 2 seconds
- No internet required
- Consistent and reproducible
- Good baseline for keyword matching

### Limitations
- Cannot understand context ("experience with models" ≠ "fashion models")
- Penalizes synonyms ("ML engineer" vs "machine learning engineer")
- Does not understand seniority requirements

---

## Algorithm 2 — LLM Matcher (Llama3)

### How It Works
Resume + Job Description → Llama3 Prompt → JSON Response
{
"llm_score": 85,
"recommendation": "APPLY",
"match_reason": "Strong Python and ML skills match core requirements",
"missing_skills": ["Docker", "MLflow"],
"strong_matches": ["Python", "NLP", "LangChain"]
}
### Prompt Engineering
We use structured prompting to ensure consistent JSON output:
1. Provide job title + company + description (truncated to 1500 chars)
2. Provide resume text (truncated to 1000 chars)
3. Request specific JSON format
4. Parse response with error handling

### Why LLM?
- Understands context and synonyms
- Can infer seniority fit
- Provides human-readable explanations
- Identifies hidden requirements

---

## Algorithm 3 — Combined Score

```python
combined_score = (fit_score * 0.4) + (llm_score * 0.6)
```

**Weight Rationale:**
- LLM gets 60% weight — more intelligent, context-aware
- TF-IDF gets 40% weight — fast baseline, keyword accuracy

---

## Recommendation Engine

| Score | Recommendation | Action |
|---|---|---|
| ≥ 70% | APPLY | Strong match — apply immediately |
| 40-69% | CONSIDER | Review carefully before applying |
| < 40% | SKIP | Significant skill gaps detected |

---

## Duplicate Detection System

### Agent 1 — In-Memory Deduplication
```python
# MD5 hash of normalized title + company
key  = f"{normalize(title)}{normalize(org)}"
hash = hashlib.md5(key.encode()).hexdigest()
# If hash seen before → duplicate
```

### Agent 2 — Database Deduplication
```python
# Check MySQL applications table
SELECT COUNT(*) FROM applications
WHERE LOWER(title)=%s AND LOWER(org)=%s
# If count > 0 → already applied
```

---

## Adaptive Pattern Learning

The system learns from every application outcome:

```python
# When application status changes to interview/offer/rejected
learn_from_application(job, outcome)

# Saves patterns to MySQL:
# - Which job titles work for your profile
# - Which companies respond
# - Which platforms are most effective
# - Which score ranges lead to interviews

# After 3+ data points, generates recommendations:
get_recommendations()
→ "Apply more on Greenhouse — highest response rate"
→ "Focus on jobs scoring 70-80% — best results"
```

---

## ATS Score

```python
# Extract keywords from JD
jd_keywords = set(re.findall(r'\b\w{4,}\b', jd_lower)) - stopwords

# Check which keywords appear in resume
matched = jd_keywords & resume_keywords

# Score = % of JD keywords found in resume
ats_score = len(matched) / len(jd_keywords) * 100
```

**Why ATS Matters:**
Most companies use Applicant Tracking Systems that scan resumes for keywords before a human ever sees them. A low ATS score means automatic rejection.