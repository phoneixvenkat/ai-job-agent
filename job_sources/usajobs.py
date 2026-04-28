import requests
import logging
log = logging.getLogger(__name__)


def fetch_usajobs(role: str, limit: int = 25) -> list:
    """Fetch US government jobs from USAJobs (no key needed for basic search)."""
    try:
        url = "https://data.usajobs.gov/api/search"
        headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": "jobpilot@example.com",
            "Authorization-Key": "",
        }
        params = {
            "Keyword": role,
            "LocationName": "United States",
            "ResultsPerPage": limit,
        }
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("SearchResult", {}).get("SearchResultItems", [])
        results = []
        for item in items:
            d = item.get("MatchedObjectDescriptor", {})
            summary = (
                d.get("UserArea", {}).get("Details", {}).get("JobSummary", "")
            )
            results.append({
                "source":      "usajobs",
                "org":         d.get("OrganizationName", "US Government"),
                "title":       d.get("PositionTitle", ""),
                "location":    d.get("PositionLocationDisplay", "USA"),
                "url":         d.get("PositionURI", ""),
                "dept":        "",
                "posted_at":   d.get("PublicationStartDate", ""),
                "description": summary[:500],
            })
        log.info(f"USAJobs: {len(results)} jobs for '{role}'")
        return results
    except Exception as e:
        log.warning(f"USAJobs failed: {e}")
        return []
