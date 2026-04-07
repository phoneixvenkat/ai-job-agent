from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import pdfplumber
import io
import os

# Internal Imports
from database import init_db, get_db, Job, Application
from job_scraper import search_jobs
from fit_scorer import calculate_fit_score, get_matching_keywords
from resume_tailor import tailor_resume, generate_cover_letter

app = FastAPI(title="AI Job Agent API")

# 1. FIXED CORS: Added both localhost and 127.0.0.1 to prevent connection refusal
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Global state (Note: In a real app, save this to a DB or File System)
resume_store = {"text": "", "filename": ""}

# --- Pydantic Schemas for Validation ---
class SearchRequest(BaseModel):
    role: str
    location: Optional[str] = "Remote"
    limit: Optional[int] = 20

class TailorRequest(BaseModel):
    job_id: int

# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "AI Job Agent API is running. Visit /docs for documentation."}

@app.post("/api/resume/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = ""
        
        if file.filename.endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = "".join([page.extract_text() or "" for page in pdf.pages])
        elif file.filename.endswith(".docx"):
            import docx
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            text = content.decode("utf-8")

        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from file.")

        resume_store["text"] = text
        resume_store["filename"] = file.filename
        
        return {
            "message": "Resume uploaded successfully", 
            "filename": file.filename, 
            "text_length": len(text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/api/jobs/search")
async def search(req: SearchRequest, db: Session = Depends(get_db)):
    if not resume_store["text"]:
        raise HTTPException(status_code=400, detail="Please upload your resume first")

    # This might be a long-running task, async is better
    jobs = search_jobs(req.role, req.location, req.limit)
    saved = []

    for j in jobs:
        fit_score = calculate_fit_score(resume_store["text"], j["description"])
        keywords = get_matching_keywords(resume_store["text"], j["description"])
        
        db_job = Job(
            title=j["title"], 
            company=j["company"], 
            location=j["location"],
            description=j["description"], 
            url=j["url"], 
            source=j["source"],
            fit_score=fit_score
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        saved.append({
            "id": db_job.id,
            "title": db_job.title,
            "company": db_job.company,
            "fit_score": db_job.fit_score,
            "keywords": keywords,
            "url": db_job.url
        })

    return {"jobs": sorted(saved, key=lambda x: x["fit_score"], reverse=True)}

@app.get("/api/jobs")
async def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.fit_score.desc()).all()
    return {"jobs": jobs}

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    apps = db.query(Application).count()
    
    avg_score = round(sum(j.fit_score for j in jobs) / len(jobs), 1) if jobs else 0
    high_fit = len([j for j in jobs if j.fit_score >= 60])
    
    return {
        "total_jobs": len(jobs), 
        "applied": apps, 
        "avg_fit_score": avg_score, 
        "high_fit_jobs": high_fit
    }

# ... (Keep tailor and apply_job routes, ensuring they use async def)