from typing import Any
from backend.agents.base_agent import BaseAgent


class ApplierAgent(BaseAgent):
    agent_name = "applier"

    def run(self, applications: list | None = None, **kwargs) -> dict[str, Any]:
        applications = applications or []
        self.log_event(f"Processing {len(applications)} applications")
        results = []
        for app in applications:
            title = app.get("title", "unknown")
            org   = app.get("org", "unknown")
            results.append({"job": f"{title} @ {org}", "status": "submitted"})
            self.log_event(f"Submitted: {title} @ {org}")
        return {"submitted": len(results), "results": results}
