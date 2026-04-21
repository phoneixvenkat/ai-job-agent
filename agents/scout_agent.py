import re
import hashlib
from job_sources.adzuna import fetch_adzuna
from job_sources.greenhouse import fetch_all_greenhouse
from job_sources.lever import fetch_all_lever
from job_sources.remotive import fetch_remotive
from job_sources.wellfound import fetch_wellfound
from job_sources.indeed_rss import fetch_indeed_rss
from job_sources.linkedin import fetch_linkedin
from job_sources.jobicy import fetch_jobicy
from job_sources.themuse import fetch_themuse
from database.mysql_db import save_jobs_to_db
from backend.utils.logger import get_logger
log = get_logger('scout')


def deduplicate(jobs: list) -> list:
    seen = set()
    unique = []
    for job in jobs:
        key = hashlib.md5(f"{job['title']}{job['org']}".lower().encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique

def match_job(job: dict, required: list, exclude: list) -> bool:
    t = f"{job['title']} {job.get('dept','')} {job['location']}".lower()
    if not all(re.search(rx.lower(), t) for rx in required): return False
    if any(re.search(rx.lower(), t) for rx in exclude): return False
    return True

def score_freshness(job: dict) -> int:
    posted = job.get("posted_at", "")
    if not posted: return 5
    posted = str(posted).lower()
    if "today" in posted or "hour" in posted: return 10
    if "1 day" in posted or "yesterday" in posted: return 9
    if "2 day" in posted: return 8
    if "3 day" in posted: return 7
    if "week" in posted and "1" in posted: return 5
    if "week" in posted: return 3
    if "month" in posted: return 1
    return 5

def run_scout(config: dict, roles: list, location: str = "Remote",
              country: str = "india") -> dict:
    log.info(f"Scout Agent starting — country={country}, roles={roles}")
    filters  = config.get("filters", {})
    sources  = config.get("sources", {})
    required = filters.get("required", [])
    exclude  = filters.get("exclude", [])
    top_n    = filters.get("top_n", 20)

    all_jobs = []

    # ── Primary: Adzuna (country-native API) ─────────────────
    for role in roles:
        log.info(f"Fetching Adzuna [{country}] for '{role}'...")
        adzuna_jobs = fetch_adzuna(role, country=country, pages=3)
        all_jobs += adzuna_jobs
    log.info(f"Adzuna total: {len(all_jobs)}")

    # ── Secondary: Remotive (worldwide remote) ────────────────
    remotive_start = len(all_jobs)
    for role in roles:
        log.info(f"Fetching Remotive for '{role}'...")
        all_jobs += fetch_remotive(role, limit=15)
    log.info(f"Remotive: {len(all_jobs) - remotive_start} jobs")

    # ── Supplemental: location-aware sources ─────────────────
    for role in roles:
        log.info(f"Fetching LinkedIn for '{role}'...")
        all_jobs += fetch_linkedin(role, location, limit=10)
        log.info(f"Fetching Jobicy for '{role}'...")
        all_jobs += fetch_jobicy(role, limit=10, location=location)
        log.info(f"Fetching TheMuse for '{role}'...")
        all_jobs += fetch_themuse(role, limit=10, location=location)

    # ── Greenhouse / Lever (config-defined orgs) ─────────────
    gh_orgs = sources.get("greenhouse", [])
    if gh_orgs:
        log.info("Fetching Greenhouse...")
        all_jobs += fetch_all_greenhouse(gh_orgs)
    lv_orgs = sources.get("lever", [])
    if lv_orgs:
        log.info("Fetching Lever...")
        all_jobs += fetch_all_lever(lv_orgs)

    log.info(f"Total fetched: {len(all_jobs)}")

    all_jobs = deduplicate(all_jobs)
    log.info(f"After deduplication: {len(all_jobs)}")

    matched = [j for j in all_jobs if match_job(j, required, exclude)]
    log.info(f"After config filtering: {len(matched)}")

    for job in matched:
        job["freshness_score"] = score_freshness(job)

    matched.sort(key=lambda x: x["freshness_score"], reverse=True)

    saved, skipped = save_jobs_to_db(matched[:top_n])
    log.info(f"[OK] Persisted {saved} new jobs ({skipped} duplicates skipped) | "
             f"Country: {country}, Adzuna: {len(adzuna_jobs)}, Total: {len(all_jobs)}")

    return {
        "status":  "success",
        "total":   len(all_jobs),
        "matched": len(matched),
        "jobs":    matched[:top_n],
        "country": country,
    }

if __name__ == "__main__":
    import yaml, pathlib
    cfg = yaml.safe_load(open("config.yaml", "r", encoding="utf-8"))
    result = run_scout(cfg, roles=["data scientist", "machine learning engineer", "AI engineer"])
    for i, job in enumerate(result["jobs"][:5], 1):
        log.info(f"{i}. {job['title']} — {job['org']} [{job['source']}] {job['freshness_score']}")