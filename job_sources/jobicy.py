import requests

def fetch_jobicy(role: str, limit: int = 15) -> list:
    """Fetch remote jobs from Jobicy's free JSON API."""
    try:
        params = {"count": min(limit, 50), "geo": "usa", "tag": role}
        r = requests.get("https://jobicy.com/api/v2/remote-jobs", params=params, timeout=15)
        data = r.json()
        jobs = []
        for job in data.get("jobs", [])[:limit]:
            jobs.append({
                "source":    "Jobicy",
                "org":       job.get("companyName", ""),
                "title":     job.get("jobTitle", ""),
                "location":  job.get("jobGeo", "Remote"),
                "url":       job.get("url", ""),
                "dept":      job.get("jobType", ""),
                "posted_at": job.get("pubDate", ""),
                "description": job.get("jobExcerpt", ""),
            })
        return jobs
    except Exception as e:
        print(f"  Jobicy error: {e}")
        return []
