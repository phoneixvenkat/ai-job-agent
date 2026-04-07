import requests
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_google_jobs(role: str, location: str = "remote", limit: int = 20) -> list:
    query   = f"{role} jobs {location}"
    url     = f"https://www.google.com/search?q={query.replace(' ','+')}&ibp=htl;jobs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        r    = requests.get(url, headers=headers, timeout=20, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        jobs = []
        for card in soup.select(".iFjolb")[:limit]:
            title   = card.select_one(".BjJfJf")
            company = card.select_one(".vNEEBe")
            loc     = card.select_one(".Qk80Jf")
            if title:
                jobs.append({
                    "source":   "Google Jobs",
                    "org":      company.get_text(strip=True) if company else "",
                    "title":    title.get_text(strip=True),
                    "location": loc.get_text(strip=True) if loc else location,
                    "url":      "",
                    "dept":     "",
                    "posted_at": ""
                })
        print(f"  Google Jobs '{role}': {len(jobs)} jobs")
        return jobs
    except Exception as e:
        print(f"  Google Jobs error: {e}")
        return []