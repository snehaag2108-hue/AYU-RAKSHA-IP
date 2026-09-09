from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import User, Innovation, Analysis, Evidence
from app.schemas.schemas import (
    RegisterRequest,
    LoginRequest,
    InnovationCreate,
    ChatRequest,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.agents.analyzer import AnalysisOrchestrator
from app.rag.retriever import rag
from app.rag.ingestion import extract_text, save_document_as_knowledge
from app.services.passport import make_passport, generate_pdf
from app.core.config import settings


router = APIRouter(prefix="/api/v1")


# =========================================================
# HEALTH
# =========================================================

@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "AYU-RAKSHA IP backend",
    }


# =========================================================
# AUTH - REGISTER
# =========================================================

@router.post("/auth/register")
def register(
    body: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == body.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    user = User(
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
        organization=body.organization,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


# =========================================================
# AUTH - OAUTH2 LOGIN
# IMPORTANT:
# Swagger Authorize uses this endpoint.
# =========================================================

@router.post(
    "/auth/login",
    include_in_schema=True,
    tags=["auth"],
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }


# =========================================================
# AUTH - JSON LOGIN
# Frontend uses this endpoint.
# =========================================================

@router.post("/auth/login-json", tags=["auth"])
def login_json(
    body: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == body.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(
        body.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }


# =========================================================
# INNOVATIONS
# =========================================================

@router.post("/innovations")
def create_innovation(
    body: InnovationCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    innovation = Innovation(
        user_id=user.id,
        **body.model_dump(),
    )

    db.add(innovation)
    db.commit()
    db.refresh(innovation)

    return {
        "id": innovation.id,
        "name": innovation.name,
        "status": "created",
    }


@router.get("/innovations")
def list_innovations(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    innovations = (
        db.query(Innovation)
        .filter(Innovation.user_id == user.id)
        .all()
    )

    return [
        {
            "id": x.id,
            "name": x.name,
            "product_type": x.product_type,
            "target_markets": x.target_markets,
            "status": "active",
        }
        for x in innovations
    ]


@router.get("/innovations/{innovation_id}")
def get_innovation(
    innovation_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    innovation = db.get(Innovation, innovation_id)

    if not innovation or innovation.user_id != user.id:
        raise HTTPException(
            status_code=404,
            detail="Innovation not found",
        )

    return {
        "id": innovation.id,
        "name": innovation.name,
        "description": innovation.description,
        "product_type": innovation.product_type,
        "ingredients": innovation.ingredients,
        "novelty": innovation.novelty,
        "source_context": innovation.source_context,
        "target_markets": innovation.target_markets,
    }


# =========================================================
# AI ANALYSIS
# =========================================================

@router.post("/innovations/{innovation_id}/analyze")
def analyze(
    innovation_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    innovation = db.get(Innovation, innovation_id)

    if not innovation or innovation.user_id != user.id:
        raise HTTPException(
            status_code=404,
            detail="Innovation not found",
        )

    result = AnalysisOrchestrator().run(innovation)

    analysis = Analysis(
        innovation_id=innovation.id,
        classification=result["classification"],
        ip_strategy=result["ip_strategy"],
        tk_assessment=result["tk_assessment"],
        abs_assessment=result["abs_assessment"],
        regulatory=result["regulatory"],
        international=result["international"],
        risks=result["risks"],
        roadmap=result["roadmap"],
        confidence=result["confidence"],
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Store evidence records
    for item in result.get("evidence", []):
        evidence = Evidence(
            analysis_id=analysis.id,
            claim="Retrieved supporting record",
            source_title=item.get("title", "Unknown"),
            source_type=item.get(
                "type",
                "knowledge_base",
            ),
            authority=item.get(
                "authority",
                "Unknown",
            ),
            jurisdiction=item.get(
                "jurisdiction",
                "General",
            ),
            version=item.get(
                "version",
                "unknown",
            ),
            passage=item.get(
                "text",
                "",
            )[:3000],
            relevance_score=item.get(
                "relevance_score",
                0,
            ),
        )

        db.add(evidence)

    db.commit()

    return {
        "analysis_id": analysis.id,
        "status": "completed",
        "result": result,
    }


# =========================================================
# ANALYSIS DETAILS
# =========================================================

@router.get("/analyses/{analysis_id}")
def get_analysis(
    analysis_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = db.get(Analysis, analysis_id)

    if (
        not analysis
        or analysis.innovation.user_id != user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    return {
        "id": analysis.id,
        "innovation_id": analysis.innovation_id,
        "classification": analysis.classification,
        "ip_strategy": analysis.ip_strategy,
        "tk_assessment": analysis.tk_assessment,
        "abs_assessment": analysis.abs_assessment,
        "regulatory": analysis.regulatory,
        "international": analysis.international,
        "risks": analysis.risks,
        "roadmap": analysis.roadmap,
        "confidence": analysis.confidence,
        "created_at": analysis.created_at,
    }


# =========================================================
# EVIDENCE
# =========================================================

@router.get("/analyses/{analysis_id}/evidence")
def evidence(
    analysis_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = db.get(Analysis, analysis_id)

    if (
        not analysis
        or analysis.innovation.user_id != user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    return [
        {
            "id": e.id,
            "claim": e.claim,
            "source_title": e.source_title,
            "source_type": e.source_type,
            "authority": e.authority,
            "jurisdiction": e.jurisdiction,
            "version": e.version,
            "passage": e.passage,
            "relevance_score": e.relevance_score,
        }
        for e in analysis.evidence
    ]


# =========================================================
# RISKS
# =========================================================

@router.get("/analyses/{analysis_id}/risks")
def risks(
    analysis_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = db.get(Analysis, analysis_id)

    if (
        not analysis
        or analysis.innovation.user_id != user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    return analysis.risks


# =========================================================
# ROADMAP
# =========================================================

@router.get("/analyses/{analysis_id}/roadmap")
def roadmap(
    analysis_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = db.get(Analysis, analysis_id)

    if (
        not analysis
        or analysis.innovation.user_id != user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    return analysis.roadmap


# =========================================================
# RAG CHAT
# =========================================================

@router.post("/chat")
def chat(
    body: ChatRequest,
    user=Depends(get_current_user),
):
    hits = rag.search(
        body.question,
        top_k=4,
    )

    if not hits:
        return {
            "answer": (
                "I could not find supporting records "
                "in the configured knowledge base. "
                "I should not invent a legal or "
                "regulatory answer."
            ),
            "confidence": {
                "level": "Low",
                "abstain": True,
            },
            "sources": [],
        }

    context = "\n\n".join(
        f"{h.get('title', 'Source')}: "
        f"{h.get('text', '')}"
        for h in hits
    )

    answer = (
        "Based on the configured knowledge base, "
        "these records appear relevant. "
        "This is evidence-oriented decision support, "
        "not a final legal conclusion.\n\n"
        + context[:5000]
    )

    sources = []

    for h in hits:
        sources.append(
            {
                "title": h.get(
                    "title",
                    "Unknown",
                ),
                "authority": h.get(
                    "authority",
                    "Unknown",
                ),
                "jurisdiction": h.get(
                    "jurisdiction",
                    "General",
                ),
                "version": h.get(
                    "version",
                    "unknown",
                ),
                "source_url": h.get(
                    "source_url"
                ),
            }
        )

    return {
        "answer": answer,
        "confidence": {
            "level": "Moderate",
            "abstain": False,
        },
        "sources": sources,
    }


# =========================================================
# DOCUMENT UPLOAD
# =========================================================

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    Path(
        settings.upload_dir
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_filename = Path(
        file.filename or "document"
    ).name

    path = (
        Path(settings.upload_dir)
        / safe_filename
    )

    content = await file.read()
    path.write_bytes(content)

    text = extract_text(str(path))

    save_document_as_knowledge(
        text,
        safe_filename,
    )

    rag.load()

    return {
        "filename": safe_filename,
        "characters_extracted": len(text),
        "note": (
            "Indexed as user-supplied context; "
            "not automatically authoritative."
        ),
    }


# =========================================================
# SOURCE SEARCH
# =========================================================

@router.get("/sources/search")
def source_search(
    q: str,
    limit: int = 5,
    user=Depends(get_current_user),
):
    safe_limit = max(
        1,
        min(limit, 20),
    )

    return rag.search(
        q,
        top_k=safe_limit,
    )


# =========================================================
# GLOBAL MARKET
# =========================================================

@router.get("/markets/{country}")
def market(
    country: str,
    user=Depends(get_current_user),
):
    return {
        "country": country,
        "status": (
            "Jurisdiction-specific review required"
        ),
        "principle": (
            "Retrieve and validate current "
            "domestic requirements separately "
            "from Indian requirements."
        ),
    }


# =========================================================
# AYU-IP PASSPORT
# =========================================================

@router.get("/passport/{innovation_id}")
def passport(
    innovation_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    innovation = db.get(
        Innovation,
        innovation_id,
    )

    if (
        not innovation
        or innovation.user_id != user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Innovation not found",
        )

    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.innovation_id
            == innovation_id
        )
        .order_by(
            Analysis.id.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Run an analysis first",
        )

    return make_passport(
        innovation,
        analysis,
    )


# =========================================================
# AYU-IP PASSPORT PDF
# =========================================================

@router.post("/passport/{innovation_id}/generate")
def passport_pdf(
    innovation_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    innovation = db.get(
        Innovation,
        innovation_id,
    )

    if (
        not innovation
        or innovation.user_id != user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Innovation not found",
        )

    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.innovation_id
            == innovation_id
        )
        .order_by(
            Analysis.id.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Run an analysis first",
        )

    pdf_path = generate_pdf(
        innovation,
        analysis,
    )

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=Path(
            pdf_path
        ).name,
    )
