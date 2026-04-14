import requests
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_wellfound(role: str, limit: int = 20) -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9"
    }
    urls = [
        f"https://wellfound.com/jobs?q={role.replace(' ','%20')}&remote=true",
        f"https://wellfound.com/jobs?q={role.replace(' ','%20')}",
        f"https://wellfound.com/role/r/{role.replace(' ','-')}"
    ]
    for url in urls:
        try:
            r    = requests.get(url, headers=headers, timeout=20, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            jobs = []
            selectors = [
                "[data-test='JobListing']",
                ".job-listing",
                "div[class*='JobListing']",
                "div[class*='job-card']"
            ]
            cards = []
            for sel in selectors:
                cards = soup.select(sel)
                if cards:
                    break

            for card in cards[:limit]:
                title   = card.select_one("[data-test='job-title']") or card.select_one("h2") or card.select_one("h3")
                company = card.select_one("[data-test='company-name']") or card.select_one("h4")
                link    = card.select_one("a")
                if title:
                    jobs.append({
                        "source":    "Wellfound",
                        "org":       company.get_text(strip=True) if company else "Startup",
                        "title":     title.get_text(strip=True),
                        "location":  "Remote",
                        "url":       "https://wellfound.com" + (link["href"] if link and link.get("href","").startswith("/") else ""),
                        "dept":      "",
                        "posted_at": ""
                    })
            if jobs:
                print(f"  Wellfound '{role}': {len(jobs)} jobs")
                return jobs
        except Exception as e:
            print(f"  Wellfound error: {e}")
            continue
    print(f"  Wellfound '{role}': 0 jobs")
    return []