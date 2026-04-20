from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ResumeBase(BaseModel):
    raw_text:    Optional[str] = None
    parsed_json: Optional[str] = None
    file_path:   Optional[str] = None


class ResumeResponse(ResumeBase):
    model_config = ConfigDict(from_attributes=True)

    id:          int
    uploaded_at: datetime


class TailorRequest(BaseModel):
    job:     dict
    use_llm: bool = False
