from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.connection import get_db
from backend.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationUpdate
from backend.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/", response_model=List[ApplicationResponse])
def list_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ApplicationService(db).list_applications(skip=skip, limit=limit)


@router.post("/", response_model=ApplicationResponse, status_code=201)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    return ApplicationService(db).create_application(payload)


@router.patch("/{app_id}", response_model=ApplicationResponse)
def update_application(app_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)):
    app = ApplicationService(db).update_status(app_id, payload.status)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app
