import requests
import logging
log = logging.getLogger(__name__)


def fetch_arbeitnow(role: str, country: str = "", limit: int = 20) -> list:
    """Fetch jobs from Arbeitnow (no API key needed)."""
    try:
        url = "https://www.arbeitnow.com/api/job-board-api"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        results = []
        country_lower = country.lower()
        for job in data:
            loc = (job.get("location") or "").lower()
            if country_lower in ("remote", "") or country_lower in loc or "remote" in loc:
                results.append({
                    "source":      "arbeitnow",
                    "org":         job.get("company_name", ""),
                    "title":       job.get("title", ""),
                    "location":    job.get("location", "Remote"),
                    "url":         job.get("url", ""),
                    "dept":        "",
                    "posted_at":   "",
                    "description": (job.get("description") or "")[:500],
                })
            if len(results) >= limit:
                break
        log.info(f"Arbeitnow: {len(results)} jobs for '{role}' / {country}")
        return results
    except Exception as e:
        log.warning(f"Arbeitnow failed: {e}")
        return []
