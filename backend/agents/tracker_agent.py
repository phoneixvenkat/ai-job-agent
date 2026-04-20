from typing import Any
from backend.agents.base_agent import BaseAgent


class TrackerAgent(BaseAgent):
    agent_name = "tracker"

    def run(self, **kwargs) -> dict[str, Any]:
        self.log_event("Checking application status updates and generating report")
        try:
            from agents.tracker_agent import generate_excel_report
            path = generate_excel_report()
            self.log_event(f"Report generated: {path}")
            return {"report_path": path, "status": "updated"}
        except Exception as e:
            self.log_event(f"Tracker failed: {e}", "ERROR")
            return {"error": str(e), "status": "failed"}
