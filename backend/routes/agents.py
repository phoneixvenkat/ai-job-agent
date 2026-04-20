from fastapi import APIRouter
from backend.schemas.agent import AgentRunRequest, AgentRunResponse
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/agents", tags=["agents"])

# Lightweight wrappers so agents can be called by name via the API
class _ScoutAgent:
    def run(self, **kwargs):
        import yaml, pathlib
        from agents.scout_agent import run_scout
        root = pathlib.Path(__file__).parent.parent.parent
        cfg  = yaml.safe_load(open(root / "config.yaml", encoding="utf-8"))
        roles = kwargs.get("roles", ["software engineer"])
        loc   = kwargs.get("location", "Remote")
        return run_scout(cfg, roles, loc)

class _AnalystAgent:
    def run(self, **kwargs):
        from agents.analyst_agent import run_analyst
        jobs   = kwargs.get("jobs", [])
        resume = kwargs.get("resume_text", "")
        return run_analyst(jobs, resume)

class _WriterAgent:
    def run(self, **kwargs):
        from agents.writer_agent import run_writer
        job    = kwargs.get("job", {})
        resume = kwargs.get("resume_text", "")
        return run_writer(job, resume)

class _EmailAgent:
    def run(self, **kwargs):
        from agents.email_agent import run_email_agent
        return run_email_agent(
            kwargs.get("email_addr", ""),
            kwargs.get("password", ""),
            kwargs.get("provider", "gmail"),
        )

class _FollowupAgent:
    def run(self, **kwargs):
        from agents.followup_agent import get_pending_followups
        return get_pending_followups()

class _InterviewPrepAgent:
    def run(self, **kwargs):
        from agents.interview_prep import generate_interview_prep
        return generate_interview_prep(kwargs.get("job", {}), kwargs.get("resume_text", ""))


AGENT_REGISTRY: dict = {
    "scout":         _ScoutAgent,
    "analyst":       _AnalystAgent,
    "writer":        _WriterAgent,
    "email":         _EmailAgent,
    "followup":      _FollowupAgent,
    "interview_prep": _InterviewPrepAgent,
}


@router.get("")
def list_agents():
    return {"agents": list(AGENT_REGISTRY.keys())}


@router.post("/run", response_model=AgentRunResponse)
def run_agent(req: AgentRunRequest):
    agent_cls = AGENT_REGISTRY.get(req.agent_name)
    if not agent_cls:
        return AgentRunResponse(
            agent_name=req.agent_name,
            status="error",
            message=f"Unknown agent: {req.agent_name}. Available: {list(AGENT_REGISTRY.keys())}",
        )
    try:
        result = agent_cls().run(**req.params)
        return AgentRunResponse(agent_name=req.agent_name, status="completed", result=result)
    except Exception as e:
        return AgentRunResponse(agent_name=req.agent_name, status="error", message=str(e))


@router.get("/status")
def all_agent_status():
    return AnalyticsService().agent_pipeline_status()


@router.post("/{name}/trigger", response_model=AgentRunResponse)
def trigger_agent(name: str):
    agent_cls = AGENT_REGISTRY.get(name)
    if not agent_cls:
        return AgentRunResponse(agent_name=name, status="error", message=f"Unknown agent: {name}")
    try:
        result = agent_cls().run()
        return AgentRunResponse(agent_name=name, status="completed", result=result)
    except Exception as e:
        return AgentRunResponse(agent_name=name, status="error", message=str(e))
