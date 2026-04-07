import requests
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_remotive(role: str, limit: int = 20) -> list:
    url = f"https://remotive.com/api/remote-jobs?search={role}&limit={limit}"
    try:
        data = requests.get(url, timeout=20, verify=False).json()
        out  = []
        for job in data.get("jobs", []):
            out.append({
                "source":   "Remotive",
                "org":      job.get("company_name", ""),
                "title":    job.get("title", ""),
                "location": job.get("candidate_required_location", "Remote"),
                "url":      job.get("url", ""),
                "dept":     job.get("category", ""),
                "posted_at": job.get("publication_date", ""),
                "description": BeautifulSoup(job.get("description", ""), "html.parser").get_text()[:2000]
            })
        print(f"  Remotive '{role}': {len(out)} jobs")
        return out
    except Exception as e:
        print(f"  Remotive error: {e}")
        return []