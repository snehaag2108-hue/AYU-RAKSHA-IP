# AYU-RAKSHA IP — SIH 2026 

A fast SIH-ready full-stack prototype for:
**“IP-SAKTI Sahayak: a multilingual, RAG-based (source-cited) AI assistant for Intellectual Property and regulatory guidance in Ayurveda, across national and international regimes.”**

## Project structure

- `backend/` — FastAPI + SQLite MVP + RAG/evidence/risk/roadmap/passport APIs
- `frontend/` — React + Vite premium UI

## Start backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

## Start frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Important

The backend is a prototype with a small demo knowledge base. It is suitable for demonstrating the architecture and end-to-end flow. For an SIH final demonstration, add authorized/current source material and validate every legal/regulatory claim.

## Demo flow

1. Register
2. Sign in
3. Open Innovation Analyzer
4. Fill an innovation
5. Analyze
6. Show TK Collision
7. Show IP Strategy
8. Show Risk Center
9. Show ABS / Regulatory
10. Show Evidence Locker
11. Show Global Market
12. Show Roadmap
13. Show AYU-IP Passport

The frontend includes the P0 navigation/features specified in the supplied frontend brief and keeps P1/P2 features lightweight so the core demo remains polished.
