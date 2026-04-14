import requests
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.google.com/"
}

def fetch_indeed_rss(role: str, location: str = "remote", limit: int = 20) -> list:
    urls = [
        f"https://www.indeed.com/rss?q={role.replace(' ','+')}&l=remote&sort=date&fromage=7",
        f"https://www.indeed.com/rss?q={role.replace(' ','+')}+remote&sort=date",
        f"https://www.indeed.com/jobs?q={role.replace(' ','+')}&l=remote&sort=date&format=rss"
    ]
    for url in urls:
        try:
            session = requests.Session()
            session.headers.update(HEADERS)
            r = session.get(url, timeout=20, verify=False)
            if r.status_code == 403:
                continue
            soup  = BeautifulSoup(r.content, "xml")
            items = soup.find_all("item")
            if not items:
                soup  = BeautifulSoup(r.content, "lxml")
                items = soup.find_all("item")
            if not items:
                continue
            jobs = []
            for item in items[:limit]:
                title   = item.find("title")
                link    = item.find("link")
                company = item.find("source")
                pubdate = item.find("pubDate")
                desc    = item.find("description")
                if not title:
                    continue
                jobs.append({
                    "source":      "Indeed",
                    "org":         company.get_text(strip=True) if company else "Unknown",
                    "title":       title.get_text(strip=True),
                    "location":    "Remote",
                    "url":         link.get_text(strip=True) if link else "",
                    "dept":        "",
                    "posted_at":   pubdate.get_text(strip=True) if pubdate else "",
                    "description": BeautifulSoup(desc.get_text(), "html.parser").get_text()[:1000] if desc else ""
                })
            if jobs:
                print(f"  Indeed '{role}': {len(jobs)} jobs")
                return jobs
        except Exception as e:
            print(f"  Indeed error: {e}")
            continue
    print(f"  Indeed '{role}': 0 jobs (blocked)")
    return []