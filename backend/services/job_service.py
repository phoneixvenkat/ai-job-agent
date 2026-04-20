from sqlalchemy.orm import Session
from backend.database.models import Job
from backend.schemas.job import JobCreate


class JobService:
    def __init__(self, db: Session):
        self.db = db

    def list_jobs(self, skip: int = 0, limit: int = 50) -> list:
        return self.db.query(Job).offset(skip).limit(limit).all()

    def get_job(self, job_id: int):
        return self.db.query(Job).filter(Job.id == job_id).first()

    def create_job(self, payload: JobCreate) -> Job:
        job = Job(**payload.model_dump())
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def search_jobs(self, params: dict) -> dict:
        query = self.db.query(Job)
        if title := params.get("title"):
            query = query.filter(Job.title.ilike(f"%{title}%"))
        if company := params.get("company"):
            query = query.filter(Job.company.ilike(f"%{company}%"))
        results = query.limit(params.get("limit", 50)).all()
        return {"jobs": results, "total": len(results)}
