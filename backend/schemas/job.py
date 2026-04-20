from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class JobBase(BaseModel):
    title:       str
    company:     Optional[str]   = None
    location:    Optional[str]   = None
    description: Optional[str]   = None
    url:         Optional[str]   = None
    platform:    Optional[str]   = None
    match_score: Optional[float] = 0.0


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id:         int
    status:     str
    created_at: datetime
