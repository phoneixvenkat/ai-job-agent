from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pdfplumber
import io
import pathlib
import yaml

from database.mysql_db import (
    init_database, log_application, get_all_applications,
    update_application_status, get_stats, check_duplicate, save_job,
    get_all_jobs, get_followup_applications,
)
from agents.scout_agent      import run_scout
from agents.analyst_agent    import run_analyst
from agents.duplicate_agent  import run_duplicate_agents
from agents.writer_agent     import run_writer
from agents.rejection_agent  import handle_rejection, handle_acceptance, handle_offer
from intelligence.adaptive_pattern import get_recommendations

# ── v1 routers ────────────────────────────────────────────
from backend.routes.jobs         import router as jobs_router
from backend.routes.applications import router as applications_router
from backend.routes.resume       import router as resume_router
from backend.routes.agents       import router as agents_router
from backend.routes.analytics    import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="JobPilot AI API",
    version="1.0.0",
    description="Multi-agent job application automation system",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── v1 versioned API ──────────────────────────────────────
app.include_router(jobs_router,         prefix="/api/v1")
app.include_router(applications_router, prefix="/api/v1")
app.include_router(resume_router,       prefix="/api/v1")
app.include_router(agents_router,       prefix="/api/v1")
app.include_router(analytics_router,    prefix="/api/v1")

# ── Health check ──────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "JobPilot AI", "version": "1.0.0"}


ROOT         = pathlib.Path(__file__).parent.parent
RESUME_CACHE = ROOT / "data" / "resume_cache.txt"
resume_store = {"text": "", "filename": ""}

if RESUME_CACHE.exists():
    resume_store["text"] = RESUME_CACHE.read_text(encoding="utf-8")


# ── Resume Upload ──────────────────────────────────────────
@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    text    = ""
    try:
        if file.filename.endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        elif file.filename.endswith(".docx"):
            import docx
            doc  = docx.Document(io.BytesIO(content))
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            text = content.decode("utf-8", errors="ignore")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read file: {str(e)}")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    resume_store["text"]     = text
    resume_store["filename"] = file.filename
    RESUME_CACHE.write_text(text, encoding="utf-8")

    return {
        "message":  "Resume uploaded successfully",
        "filename": file.filename,
        "length":   len(text),
        "preview":  text[:200]
    }


# ── Job Search ─────────────────────────────────────────────
class SearchRequest(BaseModel):
    roles:    list
    location: Optional[str] = "Remote"
    limit:    Optional[int] = 20
    use_llm:  Optional[bool] = False


@app.post("/api/jobs/search")
def search_jobs(req: SearchRequest):
    if not resume_store["text"]:
        raise HTTPException(status_code=400, detail="Upload your resume first")

    cfg    = yaml.safe_load(open(ROOT / "config.yaml", "r", encoding="utf-8"))
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

    return {
        "jobs":               analyzed,
        "total":              result["total"],
        "matched":            result["matched"],
        "duplicates_removed": dup_result["total_removed"],
        "clean_count":        dup_result["clean_count"]
    }


@app.get("/api/jobs")
def get_jobs(limit: int = 50, offset: int = 0):
    jobs, total = get_all_jobs(limit=limit, offset=offset)
    return {"success": True, "data": {"jobs": jobs, "total": total}, "error": None}


# ── Tailor Resume ──────────────────────────────────────────
class TailorRequest(BaseModel):
    job:     dict
    use_llm: Optional[bool] = True


@app.post("/api/resume/tailor")
def tailor_resume(req: TailorRequest):
    if not resume_store["text"]:
        raise HTTPException(status_code=400, detail="Upload resume first")
    result = run_writer(req.job, resume_store["text"], use_llm=req.use_llm)
    return {
        "resume_path":  result["resume_path"],
        "cover_path":   result["cover_path"],
        "cover_text":   result["cover_text"],
        "summary_used": result["summary_used"]
    }


# ── Apply to Job ───────────────────────────────────────────
class ApplyRequest(BaseModel):
    job:         dict
    resume_path: str
    cover_path:  str
    status:      Optional[str] = "applied"
    explanation: Optional[str] = ""


@app.post("/api/jobs/apply")
def apply_job(req: ApplyRequest):
    app_id = log_application(
        req.job, req.resume_path, req.cover_path,
        req.status, req.explanation
    )
    return {"message": "Application logged", "app_id": app_id}


# ── Skip Job ───────────────────────────────────────────────
class SkipRequest(BaseModel):
    job:    dict
    reason: Optional[str] = "User skipped"


@app.post("/api/jobs/skip")
def skip_job(req: SkipRequest):
    app_id = log_application(req.job, "", "", "skipped", req.reason)
    return {"message": "Job skipped", "app_id": app_id}


# ── Get Applications ───────────────────────────────────────
@app.get("/api/applications")
def get_applications():
    apps = get_all_applications()
    return {"applications": apps}


# ── Update Status ──────────────────────────────────────────
class StatusUpdate(BaseModel):
    status: str


@app.patch("/api/applications/{app_id}")
def update_status(app_id: int, update: StatusUpdate):
    update_application_status(app_id, update.status)
    return {"message": "Status updated"}


# ── Rejection / Acceptance ─────────────────────────────────
class OutcomeRequest(BaseModel):
    app_id: int
    job:    dict


@app.post("/api/applications/rejected")
def rejected(req: OutcomeRequest):
    return handle_rejection(req.app_id, req.job, resume_store["text"])


@app.post("/api/applications/accepted")
def accepted(req: OutcomeRequest):
    return handle_acceptance(req.app_id, req.job)


@app.post("/api/applications/offer")
def offer(req: OutcomeRequest):
    return handle_offer(req.app_id, req.job)


# ── Stats ──────────────────────────────────────────────────
@app.get("/api/stats")
def stats():
    s    = get_stats()
    recs = get_recommendations()
    return {**s, "recommendations": recs}


# ── Email Agent ────────────────────────────────────────────
class EmailRequest(BaseModel):
    email_addr: str
    password:   str
    provider:   Optional[str] = "gmail"


@app.post("/api/email/scan")
def scan_emails(req: EmailRequest):
    from agents.email_agent import run_email_agent
    results = run_email_agent(req.email_addr, req.password, req.provider)
    return {"results": results, "count": len(results)}


# ── Excel Report ───────────────────────────────────────────
@app.get("/api/report/excel")
def excel_report():
    from agents.tracker_agent import generate_excel_report
    path = generate_excel_report()
    return {"path": path, "message": "Report generated"}


# ── Adaptive Patterns ──────────────────────────────────────
@app.get("/api/patterns")
def patterns():
    return get_recommendations()


# ── Follow-up Agent ────────────────────────────────────────
@app.get("/api/followups")
def get_followups():
    # Applications flagged by check_followups() (no response after 7 days)
    flagged = get_followup_applications()
    # Also include agent-drafted follow-ups for pending items
    try:
        from agents.followup_agent import get_pending_followups, generate_followup_email
        pending = get_pending_followups()
        drafts  = [generate_followup_email(app) for app in pending[:5]]
    except Exception:
        drafts = []
    return {
        "success": True,
        "data": {"followups": drafts, "flagged": flagged, "count": len(drafts)},
        "error": None,
    }


@app.post("/api/followups/done/{app_id}")
def mark_done(app_id: int):
    from agents.followup_agent import mark_followup_done
    mark_followup_done(app_id)
    return {"message": "Follow-up marked done"}


# ── Interview Prep ──────────────────────────────────────────
class PrepRequest(BaseModel):
    job: dict


@app.post("/api/interview/prep")
def interview_prep(req: PrepRequest):
    from agents.interview_prep import generate_interview_prep
    result = generate_interview_prep(req.job, resume_store["text"])
    return result


# ── Orchestrator ────────────────────────────────────────────
class OrchestratorRequest(BaseModel):
    roles:    list
    location: Optional[str] = "Remote"
    use_llm:  Optional[bool] = False


@app.post("/api/orchestrate")
def orchestrate(req: OrchestratorRequest):
    if not resume_store["text"]:
        raise HTTPException(status_code=400, detail="Upload resume first")
    from agents.orchestrator import run_full_pipeline
    result = run_full_pipeline(req.roles, req.location, resume_store["text"], req.use_llm)
    return result


# ── Dry Run ─────────────────────────────────────────────────
@app.post("/api/jobs/dryrun")
def dry_run(req: SearchRequest):
    if not resume_store["text"]:
        raise HTTPException(status_code=400, detail="Upload resume first")
    cfg      = yaml.safe_load(open(ROOT / "config.yaml", "r", encoding="utf-8"))
    result   = run_scout(cfg, req.roles, req.location)
    dup      = run_duplicate_agents(result["jobs"])
    analyzed = run_analyst(dup["clean_jobs"], resume_store["text"])
    return {
        "mode":    "dry_run",
        "message": "No applications submitted",
        "jobs":    analyzed[:5],
        "total":   result["total"],
        "matched": result["matched"],
        "clean":   dup["clean_count"]
    }
