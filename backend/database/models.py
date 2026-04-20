from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.connection import Base


class Job(Base):
    __tablename__ = "jobs_v2"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(256), nullable=False)
    company     = Column(String(256))
    location    = Column(String(256))
    description = Column(Text)
    url         = Column(String(512))
    platform    = Column(String(64))
    match_score = Column(Float, default=0.0)
    status      = Column(String(32), default="new")
    created_at  = Column(DateTime, default=datetime.utcnow)

    applications = relationship("Application", back_populates="job")


class Application(Base):
    __tablename__ = "applications_v2"

    id           = Column(Integer, primary_key=True, index=True)
    job_id       = Column(Integer, ForeignKey("jobs_v2.id"), nullable=True)
    status       = Column(String(32), default="submitted")
    applied_at   = Column(DateTime, default=datetime.utcnow)
    cover_letter = Column(Text)
    notes        = Column(Text)

    job = relationship("Job", back_populates="applications")


class Resume(Base):
    __tablename__ = "resumes"

    id          = Column(Integer, primary_key=True, index=True)
    raw_text    = Column(Text)
    parsed_json = Column(Text)
    file_path   = Column(String(512))
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id           = Column(Integer, primary_key=True, index=True)
    agent_name   = Column(String(64), nullable=False)
    status       = Column(String(32), default="pending")
    message      = Column(Text)
    started_at   = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
