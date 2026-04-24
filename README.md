# Carbon Credit Tracer (CCT)
AI + Blockchain-based carbon emission verification and credit issuance system.

---

## Architecture

```
Company Report
    ↓
Baseline Lookup (IPCC table)        ← baseline = quantity × emission_factor
    ↓
AI Anomaly Detection (Isolation Forest) ← is this report suspicious?
    ↓
Credit Formula                      ← credits = baseline − reported
    ↓
MongoDB storage + Blockchain (Polygon, future)
    ↓
CCT Token Marketplace
```

## Supported materials

| Material | IPCC Factor | Source |
|---|---|---|
| Cement   | 0.90 t CO₂/t | IPCC 2006 Guidelines |
| Steel    | 1.80 t CO₂/t | World Steel Association |
| Aluminum | 11.50 t CO₂/t | IPCC 2006 Guidelines |

---

## Quick start (Docker)

```bash
git clone <repo>
cd carbon-credit-tracer
docker-compose up
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

---

## Manual setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # set your MONGODB_URL
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET  | /api/health | Health check + supported materials |
| GET  | /api/baseline-factors | IPCC emission factors |
| POST | /api/submissions/ | Submit emission report |
| GET  | /api/submissions/ | List all submissions |
| GET  | /api/submissions/{id} | Get single submission |
| GET  | /api/dashboard/stats | Aggregate stats |
| GET  | /api/dashboard/recent | Recent submissions |
| GET  | /api/dashboard/credits-by-material | Credits grouped by material |

### Example submission request
```json
POST /api/submissions/
{
  "company_name": "Acme Cement Co",
  "company_id": "ACME-001",
  "material": "cement",
  "quantity_tonnes": 1000,
  "reported_co2_tonnes": 700,
  "period": "2024-Q2"
}
```

### Example response
```json
{
  "submission_id": "uuid",
  "baseline": { "baseline_co2_tonnes": 900.0, "emission_factor": 0.9 },
  "ai_verification": { "verdict": "NORMAL", "anomaly_score": 0.12 },
  "credits": { "credits_earned": 200.0, "eligible": true },
  "final_status": "APPROVED"
}
```

---

## Project structure

```
carbon-credit-tracer/
├── backend/
│   ├── main.py                     # FastAPI app entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── app/
│       ├── models/
│       │   └── schemas.py          # Pydantic request/response models
│       ├── routes/
│       │   ├── submissions.py      # POST/GET submission endpoints
│       │   ├── dashboard.py        # Stats and analytics endpoints
│       │   └── health.py           # Health check + baseline factors
│       ├── services/
│       │   ├── ml_service.py       # Isolation Forest anomaly detector
│       │   └── credit_service.py   # Credit calculation logic
│       └── utils/
│           ├── baseline.py         # IPCC emission factor table
│           └── database.py         # MongoDB async connection
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Router setup
│   │   ├── main.jsx                # React entry point
│   │   ├── components/
│   │   │   ├── Layout.jsx          # Sidebar navigation shell
│   │   │   ├── StatCard.jsx        # Reusable stat display card
│   │   │   └── StatusBadge.jsx     # APPROVED/REJECTED/NORMAL badges
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx   # Overview stats + charts + feed
│   │   │   ├── SubmitPage.jsx      # Report form + live preview
│   │   │   ├── SubmissionsPage.jsx # Full audit table with filters
│   │   │   ├── SubmissionDetailPage.jsx  # Step-by-step verification view
│   │   │   └── MarketplacePage.jsx # CCT token trading UI
│   │   ├── utils/
│   │   │   └── api.js              # Axios API wrapper
│   │   └── styles/
│   │       └── globals.css         # Design tokens + global styles
│   ├── index.html
│   └── vite.config.js
└── docker-compose.yml
```

---

## AI model

- **Algorithm**: Isolation Forest (scikit-learn)
- **Features**: reported intensity, baseline intensity, reported/baseline ratio, material encoding
- **Training**: Synthetic data generated from IPCC factors with realistic ±15% Gaussian noise + injected fraud samples (0.1–0.4× baseline)
- **Contamination**: 10% (tunable)
- **Output**: NORMAL / SUSPICIOUS verdict + anomaly score

---

## Token economy

- **1 CCT** = 1 tonne CO₂ saved below IPCC baseline
- Tokens minted only after AI verification passes
- Each token carries: company, material, period, baseline, reported, timestamp
- Marketplace: sellers (under-emitters) ↔ buyers (over-emitters)
- Settlement: ERC-1155 on Polygon (conceptual in MVP, production-ready contract design)

---

## Future roadmap

- [ ] Polygon smart contract deployment (Hardhat + OpenZeppelin ERC-1155)
- [ ] IPFS metadata pinning (Pinata / NFT.Storage)
- [ ] IoT sensor data ingestion
- [ ] Multi-company wallet authentication
- [ ] Live marketplace smart contract
- [ ] 3-source dynamic baseline (IPCC + ML + sector peers)
