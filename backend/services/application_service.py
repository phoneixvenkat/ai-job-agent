from sqlalchemy.orm import Session
from backend.database.models import Application
from backend.schemas.application import ApplicationCreate


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def list_applications(self, skip: int = 0, limit: int = 100) -> list:
        return self.db.query(Application).offset(skip).limit(limit).all()

    def create_application(self, payload: ApplicationCreate) -> Application:
        app = Application(**payload.model_dump())
        self.db.add(app)
        self.db.commit()
        self.db.refresh(app)
        return app

    def update_status(self, app_id: int, status: str):
        app = self.db.query(Application).filter(Application.id == app_id).first()
        if not app:
            return None
        app.status = status
        self.db.commit()
        self.db.refresh(app)
        return app
