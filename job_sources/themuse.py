import requests
import urllib3
from backend.utils.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
log = get_logger("themuse")

def fetch_themuse(role: str, limit: int = 20) -> list:
    """The Muse public API — free, no auth required."""
    url = "https://www.themuse.com/api/public/jobs"
    params = {"descending": "true", "page": 0}
    try:
        r = requests.get(url, params=params, timeout=15, verify=False)
        r.raise_for_status()
        data  = r.json()
        role_lower = role.lower()
        jobs  = []
        for j in data.get("results", []):
            title = str(j.get("name", ""))
            if role_lower not in title.lower():
                continue
            company  = (j.get("company") or {}).get("name", "")
            location = ", ".join(
                loc.get("name", "") for loc in j.get("locations", [])
            ) or "Remote"
            contents = j.get("contents", "")
            from bs4 import BeautifulSoup
            desc = BeautifulSoup(contents, "html.parser").get_text()[:2000] if contents else ""
            jobs.append({
                "source":      "TheMuse",
                "org":         str(company),
                "title":       title,
                "location":    location,
                "url":         str(j.get("refs", {}).get("landing_page", "")),
                "dept":        str((j.get("categories") or [{}])[0].get("name", "")),
                "posted_at":   str(j.get("publication_date", "")),
                "description": desc,
            })
            if len(jobs) >= limit:
                break
        log.info("TheMuse '%s': %d jobs", role, len(jobs))
        return jobs
    except Exception as e:
        log.warning("TheMuse '%s' failed: %s", role, e)
        return []
