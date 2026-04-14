import requests
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_indeed_rss(role: str, location: str = "remote", limit: int = 20) -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    urls = [
        f"https://www.indeed.com/rss?q={role.replace(' ','+')}&l={location}&sort=date",
        f"https://www.indeed.com/rss?q={role.replace(' ','+')}&sort=date",
        f"https://rss.indeed.com/rss?q={role.replace(' ','+')}+remote&sort=date"
    ]
    for url in urls:
        try:
            r    = requests.get(url, headers=headers, timeout=20, verify=False)
            soup = BeautifulSoup(r.content, "xml")
            items = soup.find_all("item")
            if not items:
                soup  = BeautifulSoup(r.content, "lxml-xml")
                items = soup.find_all("item")
            jobs = []
            for item in items[:limit]:
                title   = item.find("title")
                link    = item.find("link")
                company = item.find("source")
                pubdate = item.find("pubDate")
                desc    = item.find("description")
                jobs.append({
                    "source":      "Indeed",
                    "org":         company.get_text() if company else "Unknown",
                    "title":       title.get_text() if title else "",
                    "location":    location,
                    "url":         link.get_text() if link else "",
                    "dept":        "",
                    "posted_at":   pubdate.get_text() if pubdate else "",
                    "description": BeautifulSoup(desc.get_text(), "html.parser").get_text()[:1000] if desc else ""
                })
            if jobs:
                print(f"  Indeed '{role}': {len(jobs)} jobs")
                return jobs
        except Exception as e:
            print(f"  Indeed RSS error: {e}")
            continue
    print(f"  Indeed '{role}': 0 jobs")
    return []