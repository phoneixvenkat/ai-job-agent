import requests
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

def fetch_remotive(role: str, limit: int = 20) -> list:
    # Multiple category endpoints
    endpoints = [
        f"https://remotive.com/api/remote-jobs?search={role.replace(' ','+')}&limit={limit}",
        f"https://remotive.com/api/remote-jobs?category=data&limit={limit}",
        f"https://remotive.com/api/remote-jobs?category=software-dev&limit={limit}",
        f"https://remotive.com/api/remote-jobs?category=machine-learning&limit={limit}",
    ]

    all_jobs = []
    seen     = set()

    for url in endpoints:
        try:
            r    = requests.get(url, headers=HEADERS, timeout=20, verify=False)
            if r.status_code != 200:
                continue
            data = r.json()
            jobs = data.get("jobs", [])
            for job in jobs:
                title = str(job.get("title", "")).lower()
                jid   = str(job.get("id", ""))
                if jid in seen:
                    continue
                # Filter relevant jobs
                keywords = ["data", "machine learning", "ml", "ai", "analyst",
                           "scientist", "engineer", "nlp", "python", "llm"]
                if not any(kw in title for kw in keywords):
                    continue
                seen.add(jid)
                desc = job.get("description", "")
                if isinstance(desc, str) and "<" in desc:
                    desc = BeautifulSoup(desc, "html.parser").get_text()
                all_jobs.append({
                    "source":      "Remotive",
                    "org":         str(job.get("company_name", "")),
                    "title":       str(job.get("title", "")),
                    "location":    str(job.get("candidate_required_location", "Remote")),
                    "url":         str(job.get("url", "")),
                    "dept":        str(job.get("category", "")),
                    "posted_at":   str(job.get("publication_date", "")),
                    "description": desc[:2000]
                })
        except Exception as e:
            print(f"  Remotive error: {e}")
            continue

    print(f"  Remotive '{role}': {len(all_jobs)} jobs")
    return all_jobs[:limit]