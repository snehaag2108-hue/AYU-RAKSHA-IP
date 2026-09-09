from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(60), default="researcher")
    organization = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    innovations = relationship("Innovation", back_populates="user", cascade="all, delete-orphan")

class Innovation(Base):
    __tablename__ = "innovations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    product_type = Column(String(100), default="not_sure")
    ingredients = Column(JSON, default=list)
    novelty = Column(JSON, default=list)
    source_context = Column(Text, default="")
    target_markets = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="innovations")
    analyses = relationship("Analysis", back_populates="innovation", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True)
    innovation_id = Column(Integer, ForeignKey("innovations.id"), nullable=False)
    status = Column(String(30), default="completed")
    classification = Column(JSON, default=dict)
    ip_strategy = Column(JSON, default=dict)
    tk_assessment = Column(JSON, default=dict)
    abs_assessment = Column(JSON, default=dict)
    regulatory = Column(JSON, default=dict)
    international = Column(JSON, default=dict)
    risks = Column(JSON, default=dict)
    roadmap = Column(JSON, default=list)
    confidence = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    innovation = relationship("Innovation", back_populates="analyses")
    evidence = relationship("Evidence", back_populates="analysis", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    claim = Column(Text, nullable=False)
    source_title = Column(String(255), nullable=False)
    source_type = Column(String(80), default="knowledge_base")
    authority = Column(String(255), default="Demo Knowledge Base")
    jurisdiction = Column(String(100), default="General")
    version = Column(String(100), default="demo-1")
    passage = Column(Text, nullable=False)
    relevance_score = Column(Float, default=0.0)
    analysis = relationship("Analysis", back_populates="evidence")
