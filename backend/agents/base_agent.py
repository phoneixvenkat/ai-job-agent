from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class BaseAgent(ABC):
    @property
    @abstractmethod
    def agent_name(self) -> str: ...

    @abstractmethod
    def run(self, **kwargs) -> dict[str, Any]: ...

    def get_status(self) -> dict:
        return {"agent": self.agent_name, "status": "ready"}

    def log_event(self, message: str, level: str = "INFO") -> None:
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [{level:5s}] [{self.agent_name}] {message}")
