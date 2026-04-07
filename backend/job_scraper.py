import requests
from bs4 import BeautifulSoup
import time

def scrape_remotive(role: str, limit: int = 20) -> list:
    """Scrape remote jobs from Remotive API - free and no auth needed"""
    try:
        url      = f"https://remotive.com/api/remote-jobs?search={role}&limit={limit}"
        response = requests.get(url, timeout=10)
        data     = response.json()
        jobs     = []
        for job in data.get("jobs", []):
            jobs.append({
                "title":       job.get("title", ""),
                "company":     job.get("company_name", ""),
                "location":    job.get("candidate_required_location", "Remote"),
                "description": BeautifulSoup(job.get("description", ""), "html.parser").get_text()[:2000],
                "url":         job.get("url", ""),
                "source":      "Remotive"
            })
        return jobs
    except Exception as e:
        print(f"Remotive scrape error: {e}")
        return []


def scrape_arbeitnow(role: str, limit: int = 20) -> list:
    """Scrape from Arbeitnow API - free, no auth"""
    try:
        url      = f"https://www.arbeitnow.com/api/job-board-api?search={role}"
        response = requests.get(url, timeout=10)
        data     = response.json()
        jobs     = []
        for job in data.get("data", [])[:limit]:
            jobs.append({
                "title":       job.get("title", ""),
                "company":     job.get("company_name", ""),
                "location":    job.get("location", "Remote"),
                "description": BeautifulSoup(job.get("description", ""), "html.parser").get_text()[:2000],
                "url":         job.get("url", ""),
                "source":      "Arbeitnow"
            })
        return jobs
    except Exception as e:
        print(f"Arbeitnow scrape error: {e}")
        return []


def search_jobs(role: str, location: str = "Remote", limit: int = 20) -> list:
    print(f"🔍 Searching jobs for: {role}")
    jobs = []
    jobs += scrape_remotive(role, limit)
    jobs += scrape_arbeitnow(role, limit)
    print(f"✅ Found {len(jobs)} jobs")
    return jobs[:limit]