# AYU-RAKSHA IP — SIH 2026 Backend MVP

A runnable FastAPI backend prototype for the SIH 2026 IP-SAKTI Sahayak concept.

## What is implemented
- FastAPI REST API
- JWT authentication
- User + innovation + analysis persistence
- Innovation classification
- Rule-based IP strategy engine
- Traditional Knowledge collision/similarity engine
- ABS/biodiversity assessment
- Regulatory checklist engine
- India/global jurisdiction layer (demo rule packs)
- Local RAG retrieval with TF-IDF vectors
- Evidence objects + citation metadata
- Confidence + safe-abstention logic
- Transparent risk scoring
- Roadmap/action generation
- AYU-IP Passport JSON + PDF report
- Document upload and text extraction for PDF/DOCX/TXT
- Chat endpoint grounded in the local knowledge base

## Important
The included knowledge files are **demo/sample records** so the project runs immediately. They are NOT authoritative legal sources. Before any serious demonstration or deployment, replace them with legally accessible, current, authoritative sources and preserve source/version metadata.

The system is a decision-support prototype, not legal advice.

## Run on Windows
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

## Run on Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Demo flow
1. POST `/api/v1/auth/register`
2. POST `/api/v1/auth/login` and copy the token.
3. POST `/api/v1/innovations`
4. POST `/api/v1/innovations/{id}/analyze`
5. Open the returned analysis in `/api/v1/analyses/{id}`.
6. Check `/evidence`, `/risks`, `/roadmap`.
7. GET `/api/v1/passport/{innovation_id}`.
8. POST `/api/v1/passport/{innovation_id}/generate` for a PDF.

Swagger at `/docs` lets you test every endpoint without Postman.
