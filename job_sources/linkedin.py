import requests
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_linkedin(role: str, location: str = "remote", limit: int = 20) -> list:
    url = f"https://www.linkedin.com/jobs/search/?keywords={role.replace(' ','%20')}&location={location}&f_TPR=r86400&sortBy=DD"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        r    = requests.get(url, headers=headers, timeout=20, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        jobs = []
        for card in soup.select(".job-search-card")[:limit]:
            title   = card.select_one(".base-search-card__title")
            company = card.select_one(".base-search-card__subtitle")
            loc     = card.select_one(".job-search-card__location")
            link    = card.select_one("a.base-card__full-link")
            date    = card.select_one("time")
            if title:
                jobs.append({
                    "source":   "LinkedIn",
                    "org":      company.get_text(strip=True) if company else "",
                    "title":    title.get_text(strip=True),
                    "location": loc.get_text(strip=True) if loc else location,
                    "url":      link["href"] if link else "",
                    "dept":     "",
                    "posted_at": date.get("datetime","") if date else ""
                })
        print(f"  LinkedIn '{role}': {len(jobs)} jobs")
        return jobs
    except Exception as e:
        print(f"  LinkedIn error: {e}")
        return []