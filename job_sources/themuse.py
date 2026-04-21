import requests

def fetch_themuse(role: str, limit: int = 15) -> list:
    """Fetch jobs from The Muse's free public API."""
    try:
        params = {"query": role, "page": 1, "level[]": ["Entry Level", "Mid Level", "Senior Level"]}
        r = requests.get("https://www.themuse.com/api/public/jobs", params=params, timeout=15)
        data = r.json()
        jobs = []
        for job in data.get("results", [])[:limit]:
            company = job.get("company", {}).get("name", "")
            locs    = job.get("locations", [])
            location = locs[0].get("name", "Remote") if locs else "Remote"
            jobs.append({
                "source":    "TheMuse",
                "org":       company,
                "title":     job.get("name", ""),
                "location":  location,
                "url":       job.get("refs", {}).get("landing_page", ""),
                "dept":      job.get("categories", [{}])[0].get("name", "") if job.get("categories") else "",
                "posted_at": job.get("publication_date", ""),
                "description": job.get("contents", "")[:500] if job.get("contents") else "",
            })
        return jobs
    except Exception as e:
        print(f"  TheMuse error: {e}")
        return []
