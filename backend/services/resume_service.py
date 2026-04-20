import io
from sqlalchemy.orm import Session
from fastapi import UploadFile
from backend.database.models import Resume


class ResumeService:
    def __init__(self, db: Session):
        self.db = db

    async def upload(self, file: UploadFile) -> dict:
        content = await file.read()
        text = ""
        try:
            fname = file.filename or ""
            if fname.endswith(".pdf"):
                import pdfplumber
                with pdfplumber.open(io.BytesIO(content)) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
            elif fname.endswith(".docx"):
                import docx
                doc = docx.Document(io.BytesIO(content))
                text = "\n".join(p.text for p in doc.paragraphs)
            else:
                text = content.decode("utf-8", errors="ignore")
        except Exception as e:
            return {"error": str(e)}

        resume = Resume(raw_text=text, file_path=file.filename or "")
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return {"id": resume.id, "length": len(text), "preview": text[:200]}

    def get_latest(self):
        return self.db.query(Resume).order_by(Resume.uploaded_at.desc()).first()

    def tailor(self, job: dict, use_llm: bool = False) -> dict:
        resume = self.get_latest()
        resume_text = resume.raw_text if resume else ""
        if not resume_text:
            return {"cover_text": "Upload a resume first", "resume_path": "", "cover_path": ""}
        try:
            from agents.writer_agent import run_writer
            return run_writer(job, resume_text, use_llm=use_llm)
        except Exception as e:
            return {"cover_text": f"Error: {e}", "resume_path": "", "cover_path": ""}
