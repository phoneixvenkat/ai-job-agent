![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Playwright](https://img.shields.io/badge/Playwright-Automation-brightgreen)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-lightgrey)

# 🤖 AI Job Application Agent

Automates job applications by:
- Fetching roles from **Greenhouse** & **Lever**
- Scraping job descriptions (JDs)
- Generating **tailored resumes & cover letters**
- Prefilling online application forms automatically
- Logging every application for tracking

## 🧠 Tech Stack
Python · Playwright · BeautifulSoup4 · python-docx · YAML · NLP basics

## ⚙️ Setup
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
python agent_apply.py
📂 Project Structure
ai-job-agent/
├── agent_apply.py
├── config.yaml
├── data/
│   ├── base_resume.yaml
│   ├── bullet_bank.yaml
│   └── stopwords.txt
├── out/          # generated resumes (gitignored)
├── artifacts/    # logs (gitignored)
├── requirements.txt
└── README.md
🧾 Example Output

Tailored resumes in out/

Applications logged in artifacts/applications.csv

Browser opens with prefilled details for review & submission

🪄 Features

Resume preview before upload

Auto-cleanup (no storage bloat)

Human-in-the-loop submit (safe for real use)

🚀 Future Upgrades

Fit-score ranking (TF-IDF or embeddings)

Streamlit dashboard for manual review

Email notifications for new roles

**Author:** [Venkata Sai Kumar Erla](https://www.linkedin.com/in/venkata-sai-kumar-erla-327155263/)  
**License:** MIT
