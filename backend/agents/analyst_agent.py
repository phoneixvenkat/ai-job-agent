from typing import Any
from backend.agents.base_agent import BaseAgent


class AnalystAgent(BaseAgent):
    agent_name = "analyst"

    def run(self, jobs: list | None = None, resume_text: str = "", **kwargs) -> dict[str, Any]:
        jobs = jobs or []
        self.log_event(f"Scoring {len(jobs)} jobs with TF-IDF")
        try:
            from agents.analyst_agent import run_analyst
            scored = run_analyst(jobs, resume_text)
            self.log_event(f"Scoring complete — {len(scored)} jobs scored")
            return {"jobs": scored, "total": len(scored)}
        except Exception as e:
            self.log_event(f"Analyst failed: {e}", "ERROR")
            return {"error": str(e), "jobs": [], "total": 0}
