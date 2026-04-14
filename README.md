# 🤖 JobPilot AI — Multi-Agent Job Application System

> Your personal AI recruiter that never sleeps

**MS Data Science Capstone Project | University of New Haven | 2026**
**Student:** Venkatasaikumar Erla | **Advisor:** Dr. Moin Bhuiyan

---

## 🎯 What Is JobPilot AI?

JobPilot AI is a multi-agent AI system that automates the entire job application process — from finding jobs across 5 platforms, scoring them against your resume using LLM matching, generating tailored resumes and cover letters, to tracking applications in MySQL and learning from outcomes.

---

## 🏗️ Architecture
USER → LangGraph Orchestrator → 6 AI Agents → MySQL → React Dashboard
### 6 AI Agents

| Agent | Role |
|---|---|
| 🔭 Scout Agent | Fetches jobs from Greenhouse, Lever, LinkedIn, Remotive |
| 🧪 Analyst Agent | TF-IDF fit scoring, ATS check, salary estimation |
| ✍️ Writer Agent | LLM-powered resume tailoring and cover letter generation |
| 🤖 Applier Agent | Playwright-based form filling with human behavior simulation |
| 📊 Tracker Agent | MySQL logging, Excel reports, follow-up management |
| 📧 Email Intel Agent | Gmail/Outlook scanning, interview/rejection detection |

---

## 🧠 Matching Algorithm

### How Job Matching Works

**Step 1 — TF-IDF Scoring:**
resume_text + job_description → TF-IDF vectors → cosine similarity → fit_score (0-100)

**Step 2 — LLM Matching (Optional):**
Llama3 reads JD + resume → JSON response with score, reasoning, missing skills

**Step 3 — Combined Score:**
combined = (fit_score * 0.4) + (llm_score * 0.6)

**Step 4 — Recommendation:**
- Score ≥ 70% → APPLY
- Score 40-70% → CONSIDER  
- Score < 40% → SKIP

### Duplicate Detection (2 Agents)
- **Agent 1:** In-memory MD5 hash deduplication (same title + company)
- **Agent 2:** Database check (already applied jobs filtered out)

### Adaptive Pattern Learning
System learns from application outcomes:
- Which companies respond to your profile
- Which job titles get callbacks
- Which platforms perform best
- Adjusts recommendations automatically

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | LangGraph |
| LLM | Llama3 via Ollama |
| Backend | FastAPI + Python |
| Frontend | React + TypeScript |
| Database | MySQL 8.0 |
| Job Sources | Greenhouse, Lever, LinkedIn, Remotive |
| Resume | python-docx |
| Scoring | TF-IDF + sentence-transformers |
| Reports | openpyxl |
| Auto-Apply | Playwright |

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0
- Ollama (optional, for LLM features)

### Installation

```bash
# Clone repo
git clone https://github.com/phoneixvenkat/ai-job-agent.git
cd ai-job-agent

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install && cd ..

# Setup MySQL
mysql -u root -p
CREATE DATABASE jobpilot;
EXIT;
```

### Running

**Terminal 1 — Backend:**
```bash
python -m uvicorn backend.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend && npm start
```

Open **http://localhost:3000**

---

## 📊 Features

- ✅ **258+ jobs** fetched from 4 platforms
- ✅ **LLM-based matching** using Llama3
- ✅ **Duplicate detection** with 2 dedicated agents
- ✅ **MySQL database** with 5 tables
- ✅ **Adaptive learning** from application outcomes
- ✅ **Email Intelligence** — detect interviews/rejections
- ✅ **Excel reports** with professional formatting
- ✅ **Architecture diagram** (PDF)
- ✅ **React dashboard** with animated UI

---

## 📁 Project Structure

ai-job-agent/
├── agents/           # 6 AI agents
├── database/         # MySQL connection + models
├── intelligence/     # App scorer, adaptive patterns
├── job_sources/      # Job platform scrapers
├── reports_gen/      # Excel + PDF reports
├── frontend/         # React TypeScript app
├── backend/          # FastAPI server
└── data/             # Resume YAML + bullet bank
---

## 👤 Author

**Venkatasaikumar Erla**
- GitHub: [phoneixvenkat](https://github.com/phoneixvenkat)
- LinkedIn: [venkata-sai-kumar-erla](https://www.linkedin.com/in/venkata-sai-kumar-erla-327155263/)
- Email: venkatasaikumarerla@gmail.com