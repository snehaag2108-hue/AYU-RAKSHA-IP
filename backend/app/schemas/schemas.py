from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = "researcher"
    organization: str = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class InnovationCreate(BaseModel):
    name: str
    description: str
    product_type: str = "not_sure"
    ingredients: List[str] = []
    novelty: List[str] = []
    source_context: str = ""
    target_markets: List[str] = ["India"]

class ChatRequest(BaseModel):
    question: str
    jurisdiction: str = "India"

class PassportResponse(BaseModel):
    innovation_id: int
    innovation_name: str
    readiness: int
    summary: Dict[str, Any]
