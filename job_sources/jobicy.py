import requests
import urllib3
from bs4 import BeautifulSoup
from backend.utils.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
log = get_logger("jobicy")

def fetch_jobicy(role: str, limit: int = 20) -> list:
    """Jobicy free remote jobs API — no auth required."""
    url = f"https://jobicy.com/api/v2/remote-jobs?tag={role.replace(' ', '+')}&count={limit}"
    try:
        r = requests.get(url, timeout=15, verify=False)
        r.raise_for_status()
        data = r.json()
        jobs = []
        for j in data.get("jobs", [])[:limit]:
            desc_raw = j.get("jobDescription", "") or j.get("jobExcerpt", "")
            desc = BeautifulSoup(desc_raw, "html.parser").get_text()[:2000] if desc_raw else ""
            jobs.append({
                "source":      "Jobicy",
                "org":         str(j.get("companyName", "")),
                "title":       str(j.get("jobTitle", "")),
                "location":    str(j.get("jobGeo", "Remote")),
                "url":         str(j.get("url", "")),
                "dept":        str(j.get("jobType", "")),
                "posted_at":   str(j.get("pubDate", "")),
                "description": desc,
            })
        log.info("Jobicy '%s': %d jobs", role, len(jobs))
        return jobs
    except Exception as e:
        log.warning("Jobicy '%s' failed: %s", role, e)
        return []
