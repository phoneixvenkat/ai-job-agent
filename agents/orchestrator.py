from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import yaml
import pathlib
from backend.utils.logger import get_logger
log = get_logger('orchestrator')


ROOT = pathlib.Path(__file__).parent.parent

class JobPilotState(TypedDict):
    config:       dict
    roles:        List[str]
    location:     str
    resume_text:  str
    raw_jobs:     List[dict]
    clean_jobs:   List[dict]
    analyzed_jobs:List[dict]
    matched_jobs: List[dict]
    selected_jobs:List[dict]
    written_docs: List[dict]
    applied_jobs: List[dict]
    use_llm:      bool
    status:       str
    errors:       List[str]

def scout_node(state: JobPilotState) -> JobPilotState:
    log.info("\n [Orchestrator] Running Scout Agent...")
    from agents.scout_agent import run_scout
    try:
        result         = run_scout(state["config"], state["roles"], state["location"])
        state["raw_jobs"] = result["jobs"]
        state["status"]   = f"Scout: {len(result['jobs'])} jobs found"
        log.info(f"    {len(result['jobs'])} jobs found")
    except Exception as e:
        state["errors"].append(f"Scout error: {e}")
        state["raw_jobs"] = []
    return state

def duplicate_node(state: JobPilotState) -> JobPilotState:
    log.info("\n [Orchestrator] Running Duplicate Agents...")
    from agents.duplicate_agent import run_duplicate_agents
    try:
        result             = run_duplicate_agents(state["raw_jobs"])
        state["clean_jobs"] = result["clean_jobs"]
        state["status"]     = f"Dedup: {result['clean_count']} clean jobs"
        log.info(f"    {result['clean_count']} clean jobs")
    except Exception as e:
        state["errors"].append(f"Duplicate error: {e}")
        state["clean_jobs"] = state["raw_jobs"]
    return state

def analyst_node(state: JobPilotState) -> JobPilotState:
    log.info("\n [Orchestrator] Running Analyst Agent...")
    from agents.analyst_agent import run_analyst
    try:
        state["analyzed_jobs"] = run_analyst(state["clean_jobs"], state["resume_text"])
        state["status"]        = f"Analyst: {len(state['analyzed_jobs'])} jobs scored"
        log.info(f"    {len(state['analyzed_jobs'])} jobs scored")
    except Exception as e:
        state["errors"].append(f"Analyst error: {e}")
        state["analyzed_jobs"] = state["clean_jobs"]
    return state

def llm_match_node(state: JobPilotState) -> JobPilotState:
    if not state.get("use_llm"):
        state["matched_jobs"] = state["analyzed_jobs"]
        return state
    log.info("\n [Orchestrator] Running LLM Matcher...")
    from agents.llm_matcher import batch_match
    try:
        state["matched_jobs"] = batch_match(state["resume_text"], state["analyzed_jobs"][:10])
        state["status"]       = "LLM matching complete"
        log.info(f"    LLM matching complete")
    except Exception as e:
        state["errors"].append(f"LLM match error: {e}")
        state["matched_jobs"] = state["analyzed_jobs"]
    return state

def score_node(state: JobPilotState) -> JobPilotState:
    log.info("\n [Orchestrator] Scoring applications...")
    jobs = state["matched_jobs"]
    for job in jobs:
        score = job.get("fit_score", 0)
        if score >= 70:
            job["recommendation"] = "APPLY"
            job["explanation"]    = f"Strong match at {score}% — apply now!"
        elif score >= 40:
            job["recommendation"] = "CONSIDER"
            job["explanation"]    = f"Moderate match at {score}% — worth considering."
        else:
            job["recommendation"] = "SKIP"
            job["explanation"]    = f"Low match at {score}% — significant gaps."
        job["should_apply"] = score >= 40
    state["selected_jobs"] = [j for j in jobs if j.get("should_apply")]
    state["status"]        = f"Scoring: {len(state['selected_jobs'])} recommended"
    log.info(f"    {len(state['selected_jobs'])} jobs recommended")
    return state

def should_use_llm(state: JobPilotState) -> str:
    return "llm_match" if state.get("use_llm") else "score"

def build_graph():
    workflow = StateGraph(JobPilotState)
    workflow.add_node("scout",     scout_node)
    workflow.add_node("duplicate", duplicate_node)
    workflow.add_node("analyst",   analyst_node)
    workflow.add_node("llm_match", llm_match_node)
    workflow.add_node("score",     score_node)

    workflow.set_entry_point("scout")
    workflow.add_edge("scout",     "duplicate")
    workflow.add_edge("duplicate", "analyst")
    workflow.add_conditional_edges("analyst", should_use_llm, {
        "llm_match": "llm_match",
        "score":     "score"
    })
    workflow.add_edge("llm_match", "score")
    workflow.add_edge("score",     END)

    return workflow.compile()

def run_full_pipeline(roles: list, location: str, resume_text: str, use_llm: bool = False) -> dict:
    log.info("\n JobPilot AI — LangGraph Orchestrator Starting...\n")
    cfg = yaml.safe_load(open(ROOT/"config.yaml","r",encoding="utf-8"))

    initial_state: JobPilotState = {
        "config":        cfg,
        "roles":         roles,
        "location":      location,
        "resume_text":   resume_text,
        "raw_jobs":      [],
        "clean_jobs":    [],
        "analyzed_jobs": [],
        "matched_jobs":  [],
        "selected_jobs": [],
        "written_docs":  [],
        "applied_jobs":  [],
        "use_llm":       use_llm,
        "status":        "starting",
        "errors":        []
    }

    graph  = build_graph()
    result = graph.invoke(initial_state)

    log.info(f"\n Pipeline complete!")
    print(f"   Jobs found:       {len(result['raw_jobs'])}")
    print(f"   Clean jobs:       {len(result['clean_jobs'])}")
    print(f"   Analyzed:         {len(result['analyzed_jobs'])}")
    print(f"   Recommended:      {len(result['selected_jobs'])}")
    if result["errors"]:
        print(f"   Errors:           {result['errors']}")

    return {
        "jobs":        result["matched_jobs"],
        "recommended": result["selected_jobs"],
        "total":       len(result["raw_jobs"]),
        "clean":       len(result["clean_jobs"]),
        "errors":      result["errors"],
        "status":      result["status"]
    }

if __name__ == "__main__":
    result = run_full_pipeline(
        roles       = ["Data Scientist", "ML Engineer"],
        location    = "Remote",
        resume_text = "Python machine learning data science NLP LangChain FastAPI MySQL",
        use_llm     = False
    )
    print(f"\nTop 3 recommended jobs:")
    for i, job in enumerate(result["recommended"][:3], 1):
        print(f"  {i}. {job['title']} at {job['org']} — {job['fit_score']}% fit")