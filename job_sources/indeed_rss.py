import requests
import urllib3
from bs4 import BeautifulSoup
from backend.utils.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
log = get_logger("indeed")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/",
}

_RSS_URLS = [
    "https://www.indeed.com/rss?q={q}&l=remote&sort=date&fromage=7",
    "https://www.indeed.com/rss?q={q}+remote&sort=date",
]


def fetch_indeed_rss(role: str, location: str = "remote", limit: int = 20) -> list:
    q = role.replace(" ", "+")
    for template in _RSS_URLS:
        url = template.format(q=q)
        try:
            r = requests.get(url, headers=_HEADERS, timeout=20, verify=False)
            if r.status_code == 403:
                log.warning("Indeed blocked (403) for '%s'", role)
                continue
            if r.status_code != 200:
                continue

            # Try xml parser first, fall back to lxml
            for parser in ("xml", "lxml"):
                soup  = BeautifulSoup(r.content, parser)
                items = soup.find_all("item")
                if items:
                    break

            if not items:
                continue

            jobs = []
            for item in items[:limit]:
                title_el   = item.find("title")
                link_el    = item.find("link")
                company_el = item.find("source")
                date_el    = item.find("pubDate")
                desc_el    = item.find("description")
                if not title_el:
                    continue
                desc = ""
                if desc_el:
                    desc = BeautifulSoup(desc_el.get_text(), "html.parser").get_text()[:1000]
                jobs.append({
                    "source":      "Indeed",
                    "org":         company_el.get_text(strip=True) if company_el else "Unknown",
                    "title":       title_el.get_text(strip=True),
                    "location":    "Remote",
                    "url":         link_el.get_text(strip=True) if link_el else "",
                    "dept":        "",
                    "posted_at":   date_el.get_text(strip=True) if date_el else "",
                    "description": desc,
                })

            if jobs:
                log.info("Indeed '%s': %d jobs", role, len(jobs))
                return jobs
        except Exception as e:
            log.warning("Indeed '%s' error: %s", role, e)
            continue

    log.warning("Indeed '%s': 0 jobs (blocked or no results)", role)
    return []
