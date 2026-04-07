from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./jobs.db"
engine        = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal  = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base          = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id            = Column(Integer, primary_key=True, index=True)
    title         = Column(String(256))
    company       = Column(String(256))
    location      = Column(String(256))
    description   = Column(Text)
    url           = Column(String(512))
    source        = Column(String(64))
    fit_score     = Column(Float, default=0.0)
    status        = Column(String(32), default="new")
    created_at    = Column(DateTime, default=datetime.utcnow)

class Application(Base):
    __tablename__ = "applications"
    id            = Column(Integer, primary_key=True, index=True)
    job_id        = Column(Integer)
    company       = Column(String(256))
    title         = Column(String(256))
    status        = Column(String(32), default="applied")
    fit_score     = Column(Float)
    applied_at    = Column(DateTime, default=datetime.utcnow)
    resume_path   = Column(String(512))
    cover_letter  = Column(Text)
    notes         = Column(Text)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()