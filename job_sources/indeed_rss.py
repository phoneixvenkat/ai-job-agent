import requests
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_indeed_rss(role: str, location: str = "remote", limit: int = 20) -> list:
    url = f"https://www.indeed.com/rss?q={role.replace(' ','+')}&l={location}&sort=date"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r    = requests.get(url, headers=headers, timeout=20, verify=False)
        soup = BeautifulSoup(r.content, "xml")
        jobs = []
        for item in soup.find_all("item")[:limit]:
            title   = item.find("title")
            link    = item.find("link")
            company = item.find("source")
            pubdate = item.find("pubDate")
            jobs.append({
                "source":   "Indeed",
                "org":      company.get_text() if company else "Unknown",
                "title":    title.get_text() if title else "",
                "location": location,
                "url":      link.get_text() if link else "",
                "dept":     "",
                "posted_at": pubdate.get_text() if pubdate else ""
            })
        print(f"  Indeed '{role}': {len(jobs)} jobs")
        return jobs
    except Exception as e:
        print(f"  Indeed RSS error: {e}")
        return []