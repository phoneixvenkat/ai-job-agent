import requests
import os
from backend.utils.logger import get_logger
log = get_logger('adzuna')

COUNTRY_CODES = {
    "india":         "in",
    "australia":     "au",
    "germany":       "de",
    "uk":            "gb",
    "usa":           "us",
    "united states": "us",
    "canada":        "ca",
    "singapore":     "sg",
    "uae":           "ae",
    "netherlands":   "nl",
    "france":        "fr",
    "brazil":        "br",
    "remote":        "gb",
}

def fetch_adzuna(keyword: str, country: str = "india", pages: int = 3) -> list:
    # Read at call time so load_dotenv() in the app has already run
    app_id  = os.environ.get("ADZUNA_APP_ID",  "")
    app_key = os.environ.get("ADZUNA_APP_KEY", "")

    if not app_id or not app_key or app_id == "your_app_id_here":
        log.warning("Adzuna API keys not configured — set ADZUNA_APP_ID + ADZUNA_APP_KEY in .env")
        return []

    cc   = COUNTRY_CODES.get(country.lower(), "in")
    jobs = []

    for page in range(1, pages + 1):
        try:
            url    = f"https://api.adzuna.com/v1/api/jobs/{cc}/search/{page}"
            params = {
                "app_id":           app_id,
                "app_key":          app_key,
                "what":             keyword,
                "results_per_page": 20,
                "content-type":     "application/json",
            }
            r = requests.get(url, params=params, timeout=10)
            if r.status_code != 200:
                log.error("Adzuna [%s] page %d: HTTP %d", cc, page, r.status_code)
                break
            for j in r.json().get("results", []):
                jobs.append({
                    "source":      f"adzuna_{cc}",
                    "org":         j.get("company", {}).get("display_name", ""),
                    "title":       j.get("title", ""),
                    "location":    j.get("location", {}).get("display_name", country),
                    "url":         j.get("redirect_url", ""),
                    "description": j.get("description", "")[:500],
                    "dept":        j.get("category", {}).get("label", ""),
                    "posted_at":   j.get("created", ""),
                    "salary":      {
                        "min": int(j.get("salary_min") or 0),
                        "max": int(j.get("salary_max") or 0),
                    },
                    "fit_score":   0.0,
                })
        except Exception as e:
            log.error("Adzuna error: %s", e)
            break

    log.info("Adzuna [%s]: %d jobs fetched for '%s'", cc, len(jobs), keyword)
    return jobs
