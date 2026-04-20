from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.schemas.agent import AgentRunRequest, AgentRunResponse
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/agents", tags=["agents"])

# Populated at startup when agents are registered
AGENT_REGISTRY: dict = {}


@router.post("/run", response_model=AgentRunResponse)
def run_agent(req: AgentRunRequest, db: Session = Depends(get_db)):
    agent_cls = AGENT_REGISTRY.get(req.agent_name)
    if not agent_cls:
        return AgentRunResponse(
            agent_name=req.agent_name,
            status="error",
            message=f"Unknown agent: {req.agent_name}",
        )
    result = agent_cls().run(**req.params)
    return AgentRunResponse(agent_name=req.agent_name, status="completed", result=result)


@router.get("/status")
def all_agent_status(db: Session = Depends(get_db)):
    return AnalyticsService(db).agent_pipeline_status()


@router.post("/{name}/trigger", response_model=AgentRunResponse)
def trigger_agent(name: str, db: Session = Depends(get_db)):
    agent_cls = AGENT_REGISTRY.get(name)
    if not agent_cls:
        return AgentRunResponse(agent_name=name, status="error", message=f"Unknown agent: {name}")
    result = agent_cls().run()
    return AgentRunResponse(agent_name=name, status="completed", result=result)
