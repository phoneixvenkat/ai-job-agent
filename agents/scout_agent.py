import re
import hashlib
from backend.utils.logger import get_logger
from database.mysql_db import save_jobs_to_db
from job_sources.greenhouse import fetch_all_greenhouse
from job_sources.lever import fetch_all_lever
from job_sources.remotive import fetch_remotive
from job_sources.jobicy import fetch_jobicy
from job_sources.themuse import fetch_themuse
from job_sources.indeed_rss import fetch_indeed_rss
from job_sources.linkedin import fetch_linkedin

log = get_logger("scout")


def _normalize(job: dict) -> dict:
    """Ensure every job has the canonical field set."""
    return {
        "title":       str(job.get("title", "")).strip(),
        "org":         str(job.get("org", job.get("company", ""))).strip(),
        "location":    str(job.get("location", "Remote")).strip(),
        "description": str(job.get("description", ""))[:2000],
        "source":      str(job.get("source", "")),
        "url":         str(job.get("url", "")).strip(),
        "dept":        str(job.get("dept", "")),
        "posted_at":   str(job.get("posted_at", "")),
        "match_score": float(job.get("match_score", 0.0)),
        # keep extra fields scout may have added
        **{k: v for k, v in job.items()
           if k not in ("title","org","company","location","description","source","url","dept","posted_at","match_score")},
    }


def _dedup_by_url(jobs: list) -> list:
    """Primary dedup on URL; fall back to title+org hash when URL is empty."""
    seen_urls  = set()
    seen_hash  = set()
    unique     = []
    for job in jobs:
        url = job.get("url", "").strip()
        if url:
            if url in seen_urls:
                continue
            seen_urls.add(url)
        else:
            h = hashlib.md5(f"{job['title']}{job['org']}".lower().encode()).hexdigest()
            if h in seen_hash:
                continue
            seen_hash.add(h)
        unique.append(job)
    return unique


def match_job(job: dict, required: list, exclude: list) -> bool:
    t = f"{job['title']} {job.get('dept','')} {job['location']}".lower()
    if not all(re.search(rx.lower(), t) for rx in required):
        return False
    if any(re.search(rx.lower(), t) for rx in exclude):
        return False
    return True


def score_freshness(job: dict) -> int:
    posted = str(job.get("posted_at", "")).lower()
    if not posted:
        return 5
    if "today" in posted or "hour" in posted:
        return 10
    if "1 day" in posted or "yesterday" in posted:
        return 9
    if "2 day" in posted:
        return 8
    if "3 day" in posted:
        return 7
    if "week" in posted and "1" in posted:
        return 5
    if "week" in posted:
        return 3
    if "month" in posted:
        return 1
    return 5


def run_scout(config: dict, roles: list, location: str = "Remote") -> dict:
    log.info("Scout Agent starting — roles=%s location=%s", roles, location)
    filters  = config.get("filters", {})
    sources  = config.get("sources", {})
    required = filters.get("required", [])
    exclude  = filters.get("exclude", [])
    top_n    = filters.get("top_n", 20)

    all_jobs = []
    source_counts = {}

    def _add(fetched: list, label: str):
        source_counts[label] = len(fetched)
        all_jobs.extend(fetched)
        log.info("  %-12s → %d jobs", label, len(fetched))

    # ── Static company boards (reliable APIs) ──────────
    gh_orgs = sources.get("greenhouse", [])
    if gh_orgs:
        _add(fetch_all_greenhouse(gh_orgs), "Greenhouse")

    lv_orgs = sources.get("lever", [])
    if lv_orgs:
        _add(fetch_all_lever(lv_orgs), "Lever")

    # ── Per-role sources ───────────────────────────────
    for role in roles:
        _add(fetch_remotive(role, limit=15),   f"Remotive/{role}")
        _add(fetch_jobicy(role,  limit=15),    f"Jobicy/{role}")
        _add(fetch_themuse(role, limit=10),    f"TheMuse/{role}")
        # best-effort scrapers — failures are logged inside each fetcher
        _add(fetch_linkedin(role, location, limit=15), f"LinkedIn/{role}")
        _add(fetch_indeed_rss(role, location,  limit=15), f"Indeed/{role}")

    log.info("Total fetched: %d from %d source calls", len(all_jobs), len(source_counts))

    # ── Normalize ──────────────────────────────────────
    all_jobs = [_normalize(j) for j in all_jobs]

    # ── Deduplicate by URL first ───────────────────────
    before = len(all_jobs)
    all_jobs = _dedup_by_url(all_jobs)
    log.info("After URL dedup: %d  (removed %d)", len(all_jobs), before - len(all_jobs))

    # ── Filter ────────────────────────────────────────
    matched = [j for j in all_jobs if match_job(j, required, exclude)]
    log.info("After filter: %d matched", len(matched))

    # ── Freshness sort ────────────────────────────────
    for job in matched:
        job["freshness_score"] = score_freshness(job)
    matched.sort(key=lambda x: x["freshness_score"], reverse=True)

    saved, skipped = save_jobs_to_db(matched)
    log.info("DB persist: %d saved, %d skipped (duplicates)", saved, skipped)

    log.info("Scout done — returning top %d jobs", min(len(matched), top_n))
    return {
        "status":  "success",
        "total":   len(all_jobs),
        "matched": len(matched),
        "jobs":    matched[:top_n],
        "source_counts": source_counts,
    }
