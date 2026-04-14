import requests
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROLES = [
    "machine learning", "data science", "artificial intelligence",
    "nlp", "python", "llm"
]

def fetch_remotive(role: str, limit: int = 20) -> list:
    headers = {"User-Agent": "Mozilla/5.0"}
    urls = [
        f"https://remotive.com/api/remote-jobs?search={role.replace(' ','+')}&limit={limit}",
        f"https://remotive.com/api/remote-jobs?category=data&limit={limit}",
        f"https://remotive.com/api/remote-jobs?category=software-dev&limit={limit}"
    ]
    for url in urls:
        try:
            r    = requests.get(url, headers=headers, timeout=20, verify=False)
            data = r.json()
            jobs = data.get("jobs", [])
            if not jobs:
                continue
            out = []
            for job in jobs[:limit]:
                desc = job.get("description", "")
                if isinstance(desc, str):
                    desc = BeautifulSoup(desc, "html.parser").get_text()[:2000]
                out.append({
                    "source":      "Remotive",
                    "org":         str(job.get("company_name", "")),
                    "title":       str(job.get("title", "")),
                    "location":    str(job.get("candidate_required_location", "Remote")),
                    "url":         str(job.get("url", "")),
                    "dept":        str(job.get("category", "")),
                    "posted_at":   str(job.get("publication_date", "")),
                    "description": desc
                })
            if out:
                print(f"  Remotive '{role}': {len(out)} jobs")
                return out
        except Exception as e:
            print(f"  Remotive error: {e}")
            continue
    print(f"  Remotive '{role}': 0 jobs")
    return []