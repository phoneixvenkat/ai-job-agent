import hashlib
import re
from database.mysql_db import get_connection, check_duplicate
from mysql.connector import Error
from backend.utils.logger import get_logger
log = get_logger('duplicate')


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def get_job_hash(title: str, org: str) -> str:
    key = f"{normalize(title)}{normalize(org)}"
    return hashlib.md5(key.encode()).hexdigest()

# ── Agent 1 — In-Memory Deduplicator ──────────────────
def deduplicate_in_memory(jobs: list) -> tuple:
    log.info(f"\n Duplicate Agent 1 — In-memory deduplication...")
    seen     = {}
    unique   = []
    dupes    = []

    for job in jobs:
        job_hash = get_job_hash(job["title"], job["org"])
        if job_hash in seen:
            dupes.append(job)
            print(f"  Duplicate found: {job['title']} at {job['org']} (same as {job['source']})")
        else:
            seen[job_hash] = job
            unique.append(job)

    log.info(f"   Agent 1: {len(unique)} unique | {len(dupes)} duplicates removed\n")
    return unique, dupes

# ── Agent 2 — Database Deduplicator ───────────────────
def deduplicate_against_database(jobs: list) -> tuple:
    log.info(f" Duplicate Agent 2 — Database deduplication...")
    new_jobs      = []
    already_applied = []

    for job in jobs:
        if check_duplicate(job["title"], job["org"]):
            already_applied.append(job)
            print(f"  Already applied: {job['title']} at {job['org']}")
        else:
            new_jobs.append(job)

    log.info(f"   Agent 2: {len(new_jobs)} new | {len(already_applied)} already applied\n")
    return new_jobs, already_applied

# ── Run Both Agents ────────────────────────────────────
def run_duplicate_agents(jobs: list) -> dict:
    log.info("\n Running Duplicate Detection Agents...\n")
    original_count = len(jobs)

    # Agent 1 — remove in-memory duplicates
    unique_jobs, memory_dupes = deduplicate_in_memory(jobs)

    # Agent 2 — remove already applied jobs
    new_jobs, db_dupes = deduplicate_against_database(unique_jobs)

    log.info(f" Duplicate Report:")
    print(f"   Original:        {original_count}")
    print(f"   In-memory dupes: {len(memory_dupes)}")
    print(f"   Already applied: {len(db_dupes)}")
    print(f"   Clean jobs:      {len(new_jobs)}\n")

    return {
        "clean_jobs":      new_jobs,
        "memory_dupes":    memory_dupes,
        "database_dupes":  db_dupes,
        "total_removed":   len(memory_dupes) + len(db_dupes),
        "original_count":  original_count,
        "clean_count":     len(new_jobs)
    }