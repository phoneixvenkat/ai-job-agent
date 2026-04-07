import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_wellfound(role: str, limit: int = 20) -> list:
    url = f"https://wellfound.com/jobs?q={role}&remote=true"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        from bs4 import BeautifulSoup
        r    = requests.get(url, headers=headers, timeout=20, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        jobs = []
        for card in soup.select("[data-test='JobListing']")[:limit]:
            title   = card.select_one("[data-test='job-title']")
            company = card.select_one("[data-test='company-name']")
            link    = card.select_one("a")
            if title and company:
                jobs.append({
                    "source":   "Wellfound",
                    "org":      company.get_text(strip=True),
                    "title":    title.get_text(strip=True),
                    "location": "Remote",
                    "url":      "https://wellfound.com" + (link["href"] if link else ""),
                    "dept":     "",
                    "posted_at": ""
                })
        print(f"  Wellfound '{role}': {len(jobs)} jobs")
        return jobs
    except Exception as e:
        print(f"  Wellfound error: {e}")
        return []