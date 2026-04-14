import requests
import urllib3
from bs4 import BeautifulSoup
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "sec-ch-ua": '"Google Chrome";v="120"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
}

def fetch_wellfound(role: str, limit: int = 20) -> list:
    # Try JSON API first
    api_urls = [
        f"https://wellfound.com/graphql",
        f"https://wellfound.com/api/jobs?q={role.replace(' ','+')}",
    ]

    # Try scraping with better headers
    scrape_urls = [
        f"https://wellfound.com/jobs?q={role.replace(' ','%20')}&remote=true",
        f"https://wellfound.com/jobs?q={role.replace(' ','%20')}",
        f"https://wellfound.com/role/r/{role.replace(' ','-').lower()}",
        f"https://wellfound.com/candidates/job_listings?q%5Bjob_listing_roles_role_name_cont%5D={role.replace(' ','+')}",
    ]

    session = requests.Session()
    session.headers.update(HEADERS)

    for url in scrape_urls:
        try:
            r    = session.get(url, timeout=20, verify=False)
            if r.status_code == 403:
                continue
            soup = BeautifulSoup(r.text, "html.parser")

            # Try multiple selectors
            jobs = []
            selectors = [
                "div[data-test='JobListing']",
                "[class*='job-listing']",
                "[class*='JobListing']",
                "[class*='startup-job']",
                "div[class*='styles_component']"
            ]

            cards = []
            for sel in selectors:
                cards = soup.select(sel)
                if cards:
                    break

            # Also try JSON embedded in page
            scripts = soup.find_all("script", type="application/json")
            for script in scripts:
                try:
                    data = json.loads(script.string or "")
                    if isinstance(data, dict) and "jobs" in str(data).lower():
                        # Extract jobs from JSON
                        pass
                except:
                    pass

            for card in cards[:limit]:
                title   = (card.select_one("[data-test='job-title']") or
                          card.select_one("h2") or card.select_one("h3") or
                          card.select_one("[class*='title']"))
                company = (card.select_one("[data-test='company-name']") or
                          card.select_one("h4") or card.select_one("[class*='company']"))
                link    = card.select_one("a[href]")

                if title:
                    href = ""
                    if link:
                        href = link.get("href", "")
                        if href.startswith("/"):
                            href = "https://wellfound.com" + href

                    jobs.append({
                        "source":    "Wellfound",
                        "org":       company.get_text(strip=True) if company else "Startup",
                        "title":     title.get_text(strip=True),
                        "location":  "Remote",
                        "url":       href,
                        "dept":      "",
                        "posted_at": ""
                    })

            if jobs:
                print(f"  Wellfound '{role}': {len(jobs)} jobs")
                return jobs

        except Exception as e:
            print(f"  Wellfound error: {e}")
            continue

    print(f"  Wellfound '{role}': 0 jobs (blocked)")
    return []