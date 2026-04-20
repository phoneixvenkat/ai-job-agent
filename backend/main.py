from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, Any
import asyncio
import os
import pdfplumber
import io
import pathlib
import yaml

from database.mysql_db import (
    init_database, log_application, get_all_applications,
    update_application_status, get_stats, check_duplicate, save_job,
)
from agents.scout_agent import run_scout
from agents.analyst_agent import run_analyst
from agents.duplicate_agent import run_duplicate_agents
from agents.writer_agent import run_writer
from agents.rejection_agent import handle_rejection, handle_acceptance, handle_offer
from intelligence.adaptive_pattern import get_recommendations

ROOT = pathlib.Path(__file__).parent.parent

# ── In-memory resume store (single-user local tool) ────
resume_store = {"text": "", "filename": ""}


def ok(data: Any) -> dict:
    return {"success": True, "data": data, "error": None}


def err(msg: str, status: int = 400):
    raise HTTPException(status_code=status, detail={"success": False, "data": None, "error": msg})


def load_config() -> dict:
    try:
        return yaml.safe_load(open(ROOT / "config.yaml", "r", encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "data": None, "error": f"config.yaml missing or invalid: {e}"})


async def _background_email_poll():
    while True:
        await asyncio.sleep(300)   # 5 minutes
        if not os.environ.get("EMAIL_ADDRESS") or not os.environ.get("EMAIL_PASSWORD"):
            continue
        try:
            from agents.email_agent import run_email_agent
            from database.mysql_db import check_followups
            await asyncio.to_thread(run_email_agent)
            flagged = await asyncio.to_thread(check_followups)
            if flagged:
                from backend.utils.logger import get_logger
                get_logger("main").info("Follow-up flagged for %d applications", flagged)
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    task = asyncio.create_task(_background_email_poll())
    yield
    task.cancel()


app = FastAPI(title="JobPilot AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ─────────────────────────────────────────────
@app.get("/health")
def health():
    return ok({"status": "ok"})


# ── Resume Upload ──────────────────────────────────────
@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = ""
        if file.filename.endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        elif file.filename.endswith(".docx"):
            import docx
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            text = content.decode("utf-8", errors="ignore")

        if not text.strip():
            err("Could not extract text from file")

        resume_store["text"]     = text
        resume_store["filename"] = file.filename

        return ok({
            "message":  "Resume uploaded successfully",
            "filename": file.filename,
            "length":   len(text),
            "preview":  text[:200],
        })
    except HTTPException:
        raise
    except Exception as e:
        err(f"Could not read file: {e}")


# ── Job Search ─────────────────────────────────────────
class SearchRequest(BaseModel):
    roles:    list
    location: Optional[str] = "Remote"
    limit:    Optional[int] = 20
    use_llm:  Optional[bool] = False


@app.post("/api/jobs/search")
def search_jobs(req: SearchRequest):
    try:
        if not resume_store["text"]:
            err("Upload your resume first")

        cfg    = load_config()
        result = run_scout(cfg, req.roles, req.location)
        jobs   = result["jobs"]

        dup_result = run_duplicate_agents(jobs)
        clean_jobs = dup_result["clean_jobs"]
        analyzed   = run_analyst(clean_jobs, resume_store["text"])

        for job in analyzed:
            score = job.get("fit_score", 0)
            if score >= 70:
                job["recommendation"] = "APPLY"
                job["explanation"]    = f"Strong match at {score}% — your skills align well."
            elif score >= 40:
                job["recommendation"] = "CONSIDER"
                job["explanation"]    = f"Moderate match at {score}% — worth considering."
            else:
                job["recommendation"] = "SKIP"
                job["explanation"]    = f"Low match at {score}% — skill gaps detected."
            job["combined_score"] = score
            job["should_apply"]   = score >= 40

        if req.use_llm:
            from agents.llm_matcher import batch_match
            analyzed = batch_match(resume_store["text"], analyzed[:10])

        return ok({
            "jobs":               analyzed,
            "total":              result["total"],
            "matched":            result["matched"],
            "duplicates_removed": dup_result["total_removed"],
            "clean_count":        dup_result["clean_count"],
        })
    except HTTPException:
        raise
    except Exception as e:
        err(f"Job search failed: {e}", 500)


# ── Get All Jobs ───────────────────────────────────────
@app.get("/api/jobs")
def get_jobs():
    return ok({"jobs": []})


# ── Tailor Resume ──────────────────────────────────────
class TailorRequest(BaseModel):
    job:     dict
    use_llm: Optional[bool] = False


@app.post("/api/resume/tailor")
def tailor_resume(req: TailorRequest):
    try:
        if not resume_store["text"]:
            err("Upload resume first")
        result = run_writer(req.job, resume_store["text"], use_llm=req.use_llm)
        return ok({
            "resume_path":  result["resume_path"],
            "cover_path":   result["cover_path"],
            "cover_text":   result["cover_text"],
            "summary_used": result["summary_used"],
        })
    except HTTPException:
        raise
    except Exception as e:
        err(f"Resume tailoring failed: {e}", 500)


# ── Apply to Job ───────────────────────────────────────
class ApplyRequest(BaseModel):
    job:         dict
    resume_path: str
    cover_path:  str
    status:      Optional[str] = "applied"
    explanation: Optional[str] = ""


@app.post("/api/jobs/apply")
def apply_job(req: ApplyRequest):
    try:
        app_id = log_application(
            req.job, req.resume_path, req.cover_path,
            req.status, req.explanation,
        )
        return ok({"message": "Application logged", "app_id": app_id})
    except Exception as e:
        err(f"Failed to log application: {e}", 500)


# ── Skip Job ───────────────────────────────────────────
class SkipRequest(BaseModel):
    job:    dict
    reason: Optional[str] = "User skipped"


@app.post("/api/jobs/skip")
def skip_job(req: SkipRequest):
    try:
        app_id = log_application(req.job, "", "", "skipped", req.reason)
        return ok({"message": "Job skipped", "app_id": app_id})
    except Exception as e:
        err(f"Failed to skip job: {e}", 500)


# ── Get Applications ───────────────────────────────────
@app.get("/api/applications")
def get_applications():
    try:
        apps = get_all_applications()
        return ok({"applications": apps})
    except Exception as e:
        err(f"Failed to fetch applications: {e}", 500)


# ── Update Status ──────────────────────────────────────
class StatusUpdate(BaseModel):
    status: str


@app.patch("/api/applications/{app_id}")
def update_status(app_id: int, update: StatusUpdate):
    try:
        update_application_status(app_id, update.status)
        return ok({"message": "Status updated"})
    except Exception as e:
        err(f"Failed to update status: {e}", 500)


# ── Rejection / Acceptance / Interview / Offer ─────────
class OutcomeRequest(BaseModel):
    app_id: int
    job:    dict


@app.post("/api/applications/rejected")
def rejected(req: OutcomeRequest):
    try:
        result = handle_rejection(req.app_id, req.job, resume_store["text"])
        return ok(result)
    except Exception as e:
        err(f"Rejection handler failed: {e}", 500)


@app.post("/api/applications/accepted")
def accepted(req: OutcomeRequest):
    try:
        result = handle_acceptance(req.app_id, req.job)
        return ok(result)
    except Exception as e:
        err(f"Acceptance handler failed: {e}", 500)


@app.post("/api/applications/interview")
def interview(req: OutcomeRequest):
    try:
        result = handle_acceptance(req.app_id, req.job)
        return ok(result)
    except Exception as e:
        err(f"Interview handler failed: {e}", 500)


@app.post("/api/applications/offer")
def offer(req: OutcomeRequest):
    try:
        result = handle_offer(req.app_id, req.job)
        return ok(result)
    except Exception as e:
        err(f"Offer handler failed: {e}", 500)


# ── Stats ──────────────────────────────────────────────
@app.get("/api/stats")
def stats():
    try:
        s    = get_stats()
        recs = get_recommendations()
        return ok({**s, "recommendations": recs})
    except Exception as e:
        err(f"Failed to fetch stats: {e}", 500)


# ── Email Agent ────────────────────────────────────────
class EmailRequest(BaseModel):
    email_addr: str
    password:   str
    provider:   Optional[str] = "gmail"


@app.post("/api/email/scan")
def scan_emails(req: EmailRequest):
    try:
        from agents.email_agent import run_email_agent
        results = run_email_agent(req.email_addr, req.password, req.provider)
        return ok({"results": results, "count": len(results)})
    except Exception as e:
        err(f"Email scan failed: {e}", 500)


# ── Excel Report ───────────────────────────────────────
@app.get("/api/report/excel")
def excel_report():
    try:
        from agents.tracker_agent import generate_excel_report
        path = generate_excel_report()
        return ok({"path": path, "message": "Report generated"})
    except Exception as e:
        err(f"Report generation failed: {e}", 500)


# ── Adaptive Patterns ──────────────────────────────────
@app.get("/api/patterns")
def patterns():
    try:
        return ok(get_recommendations())
    except Exception as e:
        err(f"Failed to fetch patterns: {e}", 500)


# ── Follow-up Agent ────────────────────────────────────
@app.get("/api/followups")
def get_followups():
    try:
        from agents.followup_agent import get_pending_followups, generate_followup_email
        pending = get_pending_followups()
        drafts  = [generate_followup_email(app) for app in pending[:5]]
        return ok({"followups": drafts, "count": len(drafts)})
    except Exception as e:
        err(f"Follow-up fetch failed: {e}", 500)


@app.post("/api/followups/done/{app_id}")
def mark_done(app_id: int):
    try:
        from agents.followup_agent import mark_followup_done
        mark_followup_done(app_id)
        return ok({"message": "Follow-up marked done"})
    except Exception as e:
        err(f"Failed to mark follow-up done: {e}", 500)


# ── Interview Prep ──────────────────────────────────────
class PrepRequest(BaseModel):
    job: dict


@app.post("/api/interview/prep")
def interview_prep(req: PrepRequest):
    try:
        if not resume_store["text"]:
            err("Upload resume first")
        from agents.interview_prep import generate_interview_prep
        result = generate_interview_prep(req.job, resume_store["text"])
        return ok(result)
    except HTTPException:
        raise
    except Exception as e:
        err(f"Interview prep failed: {e}", 500)


# ── Orchestrator ────────────────────────────────────────
class OrchestratorRequest(BaseModel):
    roles:    list
    location: Optional[str] = "Remote"
    use_llm:  Optional[bool] = False


@app.post("/api/orchestrate")
def orchestrate(req: OrchestratorRequest):
    try:
        if not resume_store["text"]:
            err("Upload resume first")
        from agents.orchestrator import run_full_pipeline
        result = run_full_pipeline(req.roles, req.location, resume_store["text"], req.use_llm)
        return ok(result)
    except HTTPException:
        raise
    except Exception as e:
        err(f"Orchestration failed: {e}", 500)


# ── Dry Run ─────────────────────────────────────────────
@app.post("/api/jobs/dryrun")
def dry_run(req: SearchRequest):
    try:
        if not resume_store["text"]:
            err("Upload resume first")
        cfg      = load_config()
        result   = run_scout(cfg, req.roles, req.location)
        dup      = run_duplicate_agents(result["jobs"])
        analyzed = run_analyst(dup["clean_jobs"], resume_store["text"])
        return ok({
            "mode":    "dry_run",
            "message": "No applications submitted",
            "jobs":    analyzed[:5],
            "total":   result["total"],
            "matched": result["matched"],
            "clean":   dup["clean_count"],
        })
    except HTTPException:
        raise
    except Exception as e:
        err(f"Dry run failed: {e}", 500)
