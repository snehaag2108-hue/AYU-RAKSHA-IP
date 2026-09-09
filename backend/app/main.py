from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import Base, engine
from app.models import User, Innovation, Analysis, Evidence
from app.api.routes import router

Path(settings.upload_dir).mkdir(parents=True,exist_ok=True)
Path(settings.report_dir).mkdir(parents=True,exist_ok=True)
Path(settings.knowledge_dir).mkdir(parents=True,exist_ok=True)
Base.metadata.create_all(bind=engine)

app=FastAPI(title=settings.app_name,version="0.1.0",description="SIH 2026 evidence-grounded Ayurveda IP decision-support backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ayu-raksha-ip.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

@app.get("/")
def root():
    return {"message":"AYU-RAKSHA IP backend is running","docs":"/docs"}
