from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return AnalyticsService(db).get_stats()


@router.get("/pipeline")
def get_pipeline(db: Session = Depends(get_db)):
    return AnalyticsService(db).agent_pipeline_status()
