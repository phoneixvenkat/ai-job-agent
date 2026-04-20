from typing import Any
from backend.agents.base_agent import BaseAgent


class WriterAgent(BaseAgent):
    agent_name = "writer"

    def run(
        self,
        job: dict | None = None,
        resume_text: str = "",
        use_llm: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        job = job or {}
        self.log_event(f"Generating documents for {job.get('title', 'unknown')} @ {job.get('org', '')}")
        try:
            from agents.writer_agent import run_writer
            result = run_writer(job, resume_text, use_llm=use_llm)
            self.log_event("Documents generated successfully")
            return result
        except Exception as e:
            self.log_event(f"Writer failed: {e}", "ERROR")
            return {"error": str(e), "cover_text": "", "resume_path": "", "cover_path": ""}
