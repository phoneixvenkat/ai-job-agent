"""
LangGraph-style pipeline orchestrator.

Pipeline stages (each is a node in the graph):
  Scout → Analyst → Writer → Applier → Tracker → Email

State flows forward; errors are captured per-stage and don't halt the pipeline.
"""
from typing import Any
from backend.agents.scout_agent   import ScoutAgent
from backend.agents.analyst_agent import AnalystAgent
from backend.agents.writer_agent  import WriterAgent
from backend.agents.applier_agent import ApplierAgent
from backend.agents.tracker_agent import TrackerAgent
from backend.agents.email_agent   import EmailAgent


def _build_initial_state(roles: list, location: str, resume_text: str, use_llm: bool) -> dict:
    return {
        "roles":        roles,
        "location":     location,
        "resume_text":  resume_text,
        "use_llm":      use_llm,
        "jobs":         [],
        "documents":    [],
        "applications": [],
        "errors":       [],
    }


def _run_scout(state: dict) -> dict:
    result = ScoutAgent().run(roles=state["roles"], location=state["location"])
    state["jobs"] = result.get("jobs", [])
    return state


def _run_analyst(state: dict) -> dict:
    result = AnalystAgent().run(jobs=state["jobs"], resume_text=state["resume_text"])
    state["jobs"] = result.get("jobs", state["jobs"])
    return state


def _run_writer(state: dict) -> dict:
    agent = WriterAgent()
    docs  = []
    for job in state["jobs"][:10]:
        doc = agent.run(job=job, resume_text=state["resume_text"], use_llm=state["use_llm"])
        docs.append(doc)
    state["documents"] = docs
    return state


def _run_applier(state: dict) -> dict:
    selected = [j for j in state["jobs"] if j.get("fit_score", 0) >= 70]
    result   = ApplierAgent().run(applications=selected)
    state["applications"] = result.get("results", [])
    return state


def _run_tracker(state: dict) -> dict:
    TrackerAgent().run()
    return state


def _run_email(state: dict) -> dict:
    # Email requires credentials; skipped unless provided
    return state


_STAGES = [
    ("scout",   _run_scout),
    ("analyst", _run_analyst),
    ("writer",  _run_writer),
    ("applier", _run_applier),
    ("tracker", _run_tracker),
    ("email",   _run_email),
]


def run_pipeline(
    roles: list,
    location: str = "Remote",
    resume_text: str = "",
    use_llm: bool = False,
) -> dict[str, Any]:
    state = _build_initial_state(roles, location, resume_text, use_llm)

    for stage_name, stage_fn in _STAGES:
        try:
            state = stage_fn(state)
        except Exception as e:
            state["errors"].append({"stage": stage_name, "error": str(e)})

    return {
        "status":       "completed",
        "jobs_found":   len(state["jobs"]),
        "documents":    len(state["documents"]),
        "applications": len(state["applications"]),
        "errors":       state["errors"],
    }
