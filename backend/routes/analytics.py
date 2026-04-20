from fastapi import APIRouter
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])
_svc = AnalyticsService()


@router.get("/stats")
def get_stats():
    return _svc.get_stats()


@router.get("/pipeline")
def get_pipeline():
    return _svc.agent_pipeline_status()
