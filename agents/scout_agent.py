import re
import hashlib
from job_sources.greenhouse import fetch_all_greenhouse
from job_sources.lever import fetch_all_lever
from job_sources.remotive import fetch_remotive
from job_sources.wellfound import fetch_wellfound
from job_sources.indeed_rss import fetch_indeed_rss
from job_sources.linkedin import fetch_linkedin

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

def run_scout(config: dict, roles: list, location: str = "Remote") -> dict:
    print("\n🔭 Scout Agent starting...\n")
    filters  = config.get("filters", {})
    sources  = config.get("sources", {})
    required = filters.get("required", [])
    exclude  = filters.get("exclude", [])
    top_n    = filters.get("top_n", 20)

    all_jobs = []

    # Greenhouse
    gh_orgs = sources.get("greenhouse", [])
    if gh_orgs:
        print("Fetching Greenhouse...")
        all_jobs += fetch_all_greenhouse(gh_orgs)

    # Lever
    lv_orgs = sources.get("lever", [])
    if lv_orgs:
        print("Fetching Lever...")
        all_jobs += fetch_all_lever(lv_orgs)

    # Remotive, LinkedIn, Indeed, Wellfound
    for role in roles:
        print(f"Fetching Remotive for '{role}'...")
        all_jobs += fetch_remotive(role, limit=15)
        print(f"Fetching LinkedIn for '{role}'...")
        all_jobs += fetch_linkedin(role, location, limit=15)
        print(f"Fetching Indeed for '{role}'...")
        all_jobs += fetch_indeed_rss(role, location, limit=15)
        print(f"Fetching Wellfound for '{role}'...")
        all_jobs += fetch_wellfound(role, limit=10)

    print(f"\n📦 Total fetched: {len(all_jobs)}")

    # Deduplicate
    all_jobs = deduplicate(all_jobs)
    print(f"✅ After deduplication: {len(all_jobs)}")

    # Filter
    matched = [j for j in all_jobs if match_job(j, required, exclude)]
    print(f"✅ After filtering: {len(matched)}")

    # Add freshness score
    for job in matched:
        job["freshness_score"] = score_freshness(job)

    # Sort by freshness
    matched.sort(key=lambda x: x["freshness_score"], reverse=True)

    print(f"\n🎯 Top {min(len(matched), top_n)} jobs ready\n")

    return {
        "status":    "success",
        "total":     len(all_jobs),
        "matched":   len(matched),
        "jobs":      matched[:top_n]
    }

if __name__ == "__main__":
    import yaml, pathlib
    cfg = yaml.safe_load(open("config.yaml", "r", encoding="utf-8"))
    result = run_scout(cfg, roles=["data scientist", "machine learning engineer", "AI engineer"])
    for i, job in enumerate(result["jobs"][:5], 1):
        print(f"{i}. {job['title']} — {job['org']} [{job['source']}] 🔥{job['freshness_score']}")