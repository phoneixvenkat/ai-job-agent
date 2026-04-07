import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_greenhouse(org: str) -> list:
    url = f"https://boards-api.greenhouse.io/v1/boards/{org}/jobs"
    try:
        jobs = requests.get(url, timeout=20, verify=False).json().get("jobs", [])
        out = []
        for x in jobs:
            out.append({
                "source":   "Greenhouse",
                "org":      org,
                "title":    x.get("title", ""),
                "location": ((x.get("location") or {}).get("name", "")),
                "url":      x.get("absolute_url", ""),
                "dept":     ((x.get("departments") or [{}])[0]).get("name", ""),
                "posted_at": x.get("updated_at", "")
            })
        print(f"  Greenhouse {org}: {len(out)} jobs")
        return out
    except Exception as e:
        print(f"  Greenhouse {org} error: {e}")
        return []

def fetch_all_greenhouse(orgs: list) -> list:
    all_jobs = []
    for org in orgs:
        all_jobs += fetch_greenhouse(org)
    return all_jobs