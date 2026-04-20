from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.schemas.resume import ResumeResponse, TailorRequest
from backend.services.resume_service import ResumeService

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await ResumeService(db).upload(file)


@router.get("/", response_model=ResumeResponse)
def get_resume(db: Session = Depends(get_db)):
    resume = ResumeService(db).get_latest()
    if not resume:
        raise HTTPException(status_code=404, detail="No resume uploaded yet")
    return resume


@router.post("/tailor")
def tailor_resume(req: TailorRequest, db: Session = Depends(get_db)):
    return ResumeService(db).tailor(req.job, req.use_llm)
