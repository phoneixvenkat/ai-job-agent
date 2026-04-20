from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ApplicationBase(BaseModel):
    job_id:       Optional[int] = None
    status:       str           = "submitted"
    cover_letter: Optional[str] = None
    notes:        Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: str


class ApplicationResponse(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id:         int
    applied_at: datetime
