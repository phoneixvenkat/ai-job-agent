import requests
import logging
log = logging.getLogger(__name__)


def fetch_himalayas(role: str, limit: int = 20) -> list:
    """Fetch remote jobs from Himalayas.app (no API key needed)."""
    try:
        url = "https://himalayas.app/jobs/api"
        params = {"q": role, "limit": limit}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        jobs = resp.json().get("jobs", [])
        results = []
        for job in jobs:
            company = job.get("company", {})
            org = company.get("name", "") if isinstance(company, dict) else str(company)
            results.append({
                "source":      "himalayas",
                "org":         org,
                "title":       job.get("title", ""),
                "location":    "Remote",
                "url":         job.get("applicationLink") or job.get("url", ""),
                "dept":        job.get("categorySlug", ""),
                "posted_at":   job.get("publishedAt", ""),
                "description": (job.get("description") or "")[:500],
            })
        log.info(f"Himalayas: {len(results)} jobs for '{role}'")
        return results
    except Exception as e:
        log.warning(f"Himalayas failed: {e}")
        return []
