from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class AgentRunRequest(BaseModel):
    agent_name: str
    params:     dict = {}


class AgentRunResponse(BaseModel):
    agent_name: str
    status:     str
    result:     Optional[Any] = None
    message:    str = ""


class AgentStatusResponse(BaseModel):
    agent_name:   str
    status:       str
    started_at:   Optional[datetime] = None
    completed_at: Optional[datetime] = None
    message:      Optional[str]      = None
