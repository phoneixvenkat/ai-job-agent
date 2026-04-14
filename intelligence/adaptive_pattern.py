from database.mysql_db import save_adaptive_pattern, get_adaptive_patterns

def learn_from_application(job: dict, outcome: str):
    title    = job.get("title", "").lower()
    org      = job.get("org", "").lower()
    source   = job.get("source", "").lower()
    score    = job.get("llm_score", 0)
    location = job.get("location", "").lower()

    success  = outcome in ["interview", "offer"]

    # Learn which job titles work
    save_adaptive_pattern("job_title",    title,    success)
    save_adaptive_pattern("company",      org,      success)
    save_adaptive_pattern("source",       source,   success)
    save_adaptive_pattern("score_range",  f"{int(score//10)*10}-{int(score//10)*10+10}", success)
    if "remote" in location:
        save_adaptive_pattern("location", "remote", success)

    print(f"✅ Learned from {outcome}: {title} at {org}")

def get_recommendations() -> dict:
    patterns = get_adaptive_patterns()
    recs     = {
        "best_sources":    [],
        "best_titles":     [],
        "best_score_range": "",
        "insights":        []
    }

    for p in patterns:
        ptype = p["pattern_type"]
        val   = p["pattern_value"]
        rate  = p["success_rate"]
        count = p["total_count"]

        if ptype == "source" and rate > 0.1:
            recs["best_sources"].append({"source": val, "rate": rate, "count": count})
        elif ptype == "job_title" and rate > 0.1:
            recs["best_titles"].append({"title": val, "rate": rate, "count": count})
        elif ptype == "score_range" and rate > 0.1:
            recs["best_score_range"] = val

    if recs["best_sources"]:
        top = recs["best_sources"][0]["source"]
        recs["insights"].append(f"Apply more on {top} — highest response rate")
    if recs["best_score_range"]:
        recs["insights"].append(f"Focus on jobs scoring {recs['best_score_range']}% — best results")

    return recs