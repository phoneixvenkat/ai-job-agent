from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.connection import get_db
from backend.schemas.job import JobCreate, JobResponse
from backend.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=List[JobResponse])
def list_jobs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return JobService(db).list_jobs(skip=skip, limit=limit)


@router.post("/search")
def search_jobs(payload: dict, db: Session = Depends(get_db)):
    return JobService(db).search_jobs(payload)


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    return JobService(db).create_job(payload)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = JobService(db).get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
