from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database.models import Application, AgentLog


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_stats(self) -> dict:
        total     = self.db.query(func.count(Application.id)).scalar() or 0
        submitted = self.db.query(func.count(Application.id)).filter(Application.status == "submitted").scalar() or 0
        interview = self.db.query(func.count(Application.id)).filter(Application.status == "interviewing").scalar() or 0
        offer     = self.db.query(func.count(Application.id)).filter(Application.status == "offer").scalar() or 0
        rejected  = self.db.query(func.count(Application.id)).filter(Application.status == "rejected").scalar() or 0
        return {
            "total":     total,
            "applied":   submitted,
            "interview": interview,
            "offer":     offer,
            "rejected":  rejected,
        }

    def agent_pipeline_status(self) -> list:
        logs = (
            self.db.query(AgentLog)
            .order_by(AgentLog.started_at.desc())
            .limit(20)
            .all()
        )
        return [
            {
                "agent_name": log.agent_name,
                "status":     log.status,
                "message":    log.message,
                "started_at": log.started_at,
            }
            for log in logs
        ]
