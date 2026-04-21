import requests

# Maps common location strings to Jobicy geo codes
_GEO_MAP = {
    "india":         "india",
    "remote":        "",
    "usa":           "usa",
    "united states": "usa",
    "uk":            "uk",
    "united kingdom":"uk",
    "canada":        "canada",
    "germany":       "germany",
    "australia":     "australia",
}

def fetch_jobicy(role: str, limit: int = 15, location: str = "") -> list:
    """Fetch remote jobs from Jobicy's free JSON API."""
    try:
        geo = ""
        if location:
            geo = _GEO_MAP.get(location.lower(), location.lower())

        params: dict = {"count": min(limit, 50), "tag": role}
        if geo:
            params["geo"] = geo

        r = requests.get("https://jobicy.com/api/v2/remote-jobs", params=params, timeout=15)
        data = r.json()
        jobs = []
        for job in data.get("jobs", [])[:limit]:
            jobs.append({
                "source":      "Jobicy",
                "org":         job.get("companyName", ""),
                "title":       job.get("jobTitle", ""),
                "location":    job.get("jobGeo", location or "Remote"),
                "url":         job.get("url", ""),
                "dept":        job.get("jobType", ""),
                "posted_at":   job.get("pubDate", ""),
                "description": job.get("jobExcerpt", ""),
            })
        return jobs
    except Exception as e:
        print(f"  Jobicy error: {e}")
        return []
