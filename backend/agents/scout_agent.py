import pathlib
import yaml
from typing import Any
from backend.agents.base_agent import BaseAgent

_CONFIG_PATH = pathlib.Path(__file__).parents[3] / "config.yaml"


class ScoutAgent(BaseAgent):
    agent_name = "scout"

    def run(self, roles: list | None = None, location: str = "Remote", **kwargs) -> dict[str, Any]:
        self.log_event(f"Scouting roles={roles}, location={location}")
        try:
            cfg    = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8"))
            from agents.scout_agent import run_scout
            result = run_scout(cfg, roles or ["Data Scientist"], location)
            self.log_event(f"Found {result.get('total', 0)} jobs across {result.get('matched', 0)} matched")
            return result
        except Exception as e:
            self.log_event(f"Scout failed: {e}", "ERROR")
            return {"error": str(e), "jobs": [], "total": 0, "matched": 0}
