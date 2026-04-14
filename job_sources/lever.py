import requests
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Verified working Lever companies
LEVER_COMPANIES = [
    "netflix",
    "stripe",
    "figma",
    "notion",
    "airtable",
    "brex",
    "plaid",
    "robinhood",
    "chime",
    "carta",
    "lattice",
    "linear",
    "retool",
    "vercel",
    "posthog",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

def fetch_lever(org: str) -> list:
    url = f"https://api.lever.co/v0/postings/{org}?mode=json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        if r.status_code == 404:
            return []
        if r.status_code != 200:
            return []
        data = r.json()
        if not isinstance(data, list):
            return []
        out = []
        for p in data:
            if not isinstance(p, dict):
                continue
            cat = p.get("categories") or {}
            if not isinstance(cat, dict):
                cat = {}
            title = str(p.get("text", ""))
            out.append({
                "source":      "Lever",
                "org":         org,
                "title":       title,
                "location":    str(cat.get("location", "") or p.get("workplaceType", "") or ""),
                "url":         str(p.get("hostedUrl", "")),
                "dept":        str(cat.get("team", "")),
                "posted_at":   str(p.get("createdAt", "")),
                "description": str(p.get("descriptionPlain", ""))[:2000]
            })
        if out:
            print(f"  Lever {org}: {len(out)} jobs")
        return out
    except Exception as e:
        print(f"  Lever {org} error: {e}")
        return []

def fetch_all_lever(orgs: list) -> list:
    all_jobs = []
    for org in orgs:
        jobs = fetch_lever(org)
        all_jobs += jobs
        time.sleep(0.5)
    return all_jobs