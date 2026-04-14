import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LEVER_COMPANIES = [
    "netflix", "twitter", "uber", "airbnb", "stripe",
    "coinbase", "figma", "notion", "airtable", "scale-ai",
    "anthropic", "openai", "cohere", "huggingface", "weights-biases",
    "dataiku", "labelbox", "snorkel-ai", "activeloop", "dbtlabs"
]

def fetch_lever(org: str) -> list:
    url     = f"https://api.lever.co/v0/postings/{org}?mode=json"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        if response.status_code != 200:
            return []
        data = response.json()
        if not isinstance(data, list):
            return []
        out = []
        for p in data:
            if not isinstance(p, dict):
                continue
            cat = p.get("categories") or {}
            if not isinstance(cat, dict):
                cat = {}
            out.append({
                "source":    "Lever",
                "org":       org,
                "title":     str(p.get("text", "")),
                "location":  str(cat.get("location", "") or p.get("workplaceType", "") or ""),
                "url":       str(p.get("hostedUrl", "")),
                "dept":      str(cat.get("team", "")),
                "posted_at": str(p.get("createdAt", "")),
                "description": str(p.get("descriptionPlain", "") or p.get("description", ""))[:2000]
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