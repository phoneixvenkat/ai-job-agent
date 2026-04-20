from typing import Any
from backend.agents.base_agent import BaseAgent


class EmailAgent(BaseAgent):
    agent_name = "email"

    def run(
        self,
        email_addr: str = "",
        password: str = "",
        provider: str = "gmail",
        **kwargs,
    ) -> dict[str, Any]:
        self.log_event(f"Scanning {provider} inbox for {email_addr or 'configured account'}")
        try:
            from agents.email_agent import run_email_agent
            results = run_email_agent(email_addr, password, provider)
            self.log_event(f"Found {len(results)} recruiter threads")
            return {"results": results, "count": len(results)}
        except Exception as e:
            self.log_event(f"Email scan failed: {e}", "ERROR")
            return {"error": str(e), "results": [], "count": 0}
