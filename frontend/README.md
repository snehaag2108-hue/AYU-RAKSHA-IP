# AYU-RAKSHA IP Frontend

React + Vite frontend for the SIH 2026 AYU-RAKSHA IP decision-support platform.

## Run

```bash
npm install
npm run dev
```

Open http://localhost:5173

The frontend expects the FastAPI backend at:

`http://127.0.0.1:8000`

You can override it with `.env`:

```env
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

## Main demo flow

Dashboard → Innovation Analyzer → AI Analysis → Traditional Knowledge → IP Strategy → Risk → ABS/Regulatory → Evidence → Global Market → Roadmap → AYU-IP Passport.

The UI is intentionally designed around the supplied frontend brief and the reference video's visual language: warm ivory background, dark botanical green, serif editorial headings, rounded cards, soft borders, and a calm premium Ayurveda aesthetic.

Important: the included backend uses demo knowledge records. Replace them with authorized/current authoritative sources before presenting legal or regulatory outputs as real-world conclusions.
