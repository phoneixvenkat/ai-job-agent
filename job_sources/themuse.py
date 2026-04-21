import requests

def fetch_themuse(role: str, limit: int = 15, location: str = "") -> list:
    """Fetch jobs from The Muse's free public API."""
    try:
        params: dict = {"query": role, "page": 1,
                        "level[]": ["Entry Level", "Mid Level", "Senior Level"]}
        if location and location.lower() not in ("remote", "anywhere", ""):
            params["location[]"] = location

        r = requests.get("https://www.themuse.com/api/public/jobs", params=params, timeout=15)
        data = r.json()
        jobs = []
        for job in data.get("results", [])[:limit]:
            company  = job.get("company", {}).get("name", "")
            locs     = job.get("locations", [])
            loc_name = locs[0].get("name", location or "Remote") if locs else (location or "Remote")
            jobs.append({
                "source":      "TheMuse",
                "org":         company,
                "title":       job.get("name", ""),
                "location":    loc_name,
                "url":         job.get("refs", {}).get("landing_page", ""),
                "dept":        job.get("categories", [{}])[0].get("name", "") if job.get("categories") else "",
                "posted_at":   job.get("publication_date", ""),
                "description": (job.get("contents") or "")[:500],
            })
        return jobs
    except Exception as e:
        print(f"  TheMuse error: {e}")
        return []
