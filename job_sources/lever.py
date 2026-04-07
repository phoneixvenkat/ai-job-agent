import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_lever(org: str) -> list:
    url = f"https://api.lever.co/v0/postings/{org}?mode=json"
    try:
        response = requests.get(url, timeout=20, verify=False)
        posts = response.json()
        if not isinstance(posts, list):
            print(f"  Lever {org}: unexpected response")
            return []
        out = []
        for p in posts:
            cat = p.get("categories") or {}
            out.append({
                "source":   "Lever",
                "org":      org,
                "title":    p.get("text", ""),
                "location": cat.get("location", "") or (p.get("workplaceType") or ""),
                "url":      p.get("hostedUrl", ""),
                "dept":     cat.get("team", ""),
                "posted_at": str(p.get("createdAt", ""))
            })
        print(f"  Lever {org}: {len(out)} jobs")
        return out
    except Exception as e:
        print(f"  Lever {org} error: {e}")
        return []

def fetch_all_lever(orgs: list) -> list:
    all_jobs = []
    for org in orgs:
        all_jobs += fetch_lever(org)
    return all_jobs