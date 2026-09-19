# EkMat — National Material Harmonization Platform
## AI-Driven Standardization & Entity Resolution for Central Public Sector Enterprises (CPSEs)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC.svg)](https://tailwindcss.com/)
[![pgvector](https://img.shields.io/badge/Vector%20DB-PostgreSQL%20%2B%20pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Overview & Problem Statement

Indian Central Public Sector Enterprises (CPSEs)—such as **BHEL, ONGC, GAIL, NTPC, and SAIL**—operate large-scale independent SAP ECC and S/4HANA instances. Over decades of decentralized plant-level procurement, identical engineering components have been cataloged under conflicting internal item codes, disparate abbreviations (*CS vs Carbon Steel*, *6IN vs 150MM*, *150# vs Class 150*), and inconsistent units of measure.

This catalog fragmentation leads to:
- **Duplicate Procurement:** Multiple CPSEs buying the same components independently without volume leverage.
- **Inflated Working Capital:** High inventory holding costs and redundant safety stocks across nearby plants.
- **Zero Cross-CPSE Traceability:** Inability to share or transfer critical spares during plant emergency shutdowns.

**EkMat** solves this by acting as an intelligent, governed entity resolution and harmonization platform. It reads master records across disparate CPSE ERP systems, identifies duplicate and equivalent materials through a transparent multi-signal AI engine, mints an authoritative **Common National Material Code**, and preserves 100% backward traceability to all original legacy codes—all through a strictly audited, human-approved workflow.

> 📖 **In-Depth Roadmap & Architecture Whitepaper:**  
> For the comprehensive executive and technical breakdown on scaling this prototype to millions of records across 50+ CPSEs (including SAP RFC/BAPI connectors, Kafka event streaming, DPDP Act compliance, and GeM integration), see **[`REAL_WORLD_IMPLEMENTATION_ROADMAP.md`](./REAL_WORLD_IMPLEMENTATION_ROADMAP.md)**.

---

## 2. Core Architecture & Pipeline

```
                                  ┌───────────────────────────────┐
                                  │   CPSE SAP / ERP Master Data  │
                                  │  (BHEL, ONGC, GAIL, NTPC, SAIL)│
                                  └───────────────┬───────────────┘
                                                  │ (CSV Ingestion / REST API)
                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FASTAPI BACKEND CORE                                          │
│                                                                                                 │
│  ┌───────────────────────┐   ┌────────────────────────┐   ┌──────────────────────────────────┐  │
│  │   1. Preprocessing    │──▶│  2. Category Blocking  │──▶│    3. AI Multi-Signal Engine     │  │
│  │ Case/Unit/Abbreviation│   │ Prunes O(N²) search    │   │  • SBERT (384-d Cosine)  [50%]   │  │
│  │ Normalization (MS/CS) │   │ space by domain        │   │  • RapidFuzz Lexical     [30%]   │  │
│  └───────────────────────┘   └────────────────────────┘   │  • Technical Attributes  [20%]   │  │
│                                                           └────────────────┬─────────────────┘  │
│                                                                            │                    │
│                                                                            ▼                    │
│  ┌───────────────────────┐   ┌────────────────────────┐   ┌──────────────────────────────────┐  │
│  │  6. National Code Gen │◀──│ 5. Human-in-the-Loop   │◀──│   4. Confidence Routing          │  │
│  │ EKMAT-{CAT}-{MAT}-... │   │ Approve / Edit / Reject│   │  • HIGH (>90%): Suggested        │  │
│  └───────────┬───────────┘   └───────────┬────────────┘   │  • MEDIUM (60-90%): Human Review │  │
│              │                           │                │  • LOW (<60%): Distinct Physical │  │
│              │                           │                └──────────────────────────────────┘  │
└──────────────┼───────────────────────────┼──────────────────────────────────────────────────────┘
               ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               PERSISTENCE LAYER (POSTGRESQL / SQLITE)                           │
│  • cpse               • materials (VECTOR 384)   • candidate_matches (status index)            │
│  • common_materials   • cpse_mappings (trace)    • audit_log (immutable governance ledger)      │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Technical Pillars
1. **Domain Abbreviation & Unit Normalization:** Deterministic engineering lookup tables (`CS` $\rightarrow$ `CARBON STEEL`, `WNRF` $\rightarrow$ `WELD NECK RAISED FACE`, `6IN` $\leftrightarrow$ `150MM`, `150#` $\leftrightarrow$ `CLASS 150`).
2. **Category Blocking:** Prunes exhaustive $O(N^2)$ comparisons into domain blocks (`VALVE`, `BEARING`, `PUMP`, `FLANGE`).
3. **Multi-Signal Scoring Formula:**
   $$\text{Weighted Score} = 0.50 \times \text{Semantic} + 0.30 \times \text{Fuzzy} + 0.20 \times \text{Attributes}$$
   - **Semantic (50%):** SBERT (`all-MiniLM-L6-v2`) 384-dimensional dense embeddings with cosine similarity.
   - **Lexical (30%):** RapidFuzz token sort and token set ratios for word-order invariance.
   - **Specification (20%):** Rule-based and Ollama/Llama 3 attribute extraction (Size, Rating, Material, Type).
4. **Non-Overmatching Compatibility Guard:** A strict `are_materials_compatible()` guard prevents transitive chaining and near-miss overmerging (e.g. 6" Gate Valve vs 6" Globe Valve scored at 0.14 and strictly isolated).
5. **Deterministic Code Minting:** Mints structured national codes: `EKMAT-{CATEGORY}-{MATERIAL}-{SPEC}-{SEQUENCE}`.
6. **Reverse Traceability:** Dedicated `cpse_mappings` join table maintains bidirectional lookup between legacy ERP codes and national codes.
7. **Immutable Audit Ledger:** Every mutation (`APPROVE`, `EDIT_APPROVE`, `REJECT`) records before/after JSON diffs.

---

## 3. Defensible Benchmark Proof & Accuracy

EkMat was evaluated against a 186-material ground-truth dataset (`data/seed/cpse_seed.csv`) containing 52 known equivalence clusters and deliberate near-miss test pairs:

| Evaluation Metric | Mathematical Formula | Target Standard | Measured Prototype Result | Status |
|---|---|---|---|---|
| **Precision** | $\frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$ | $\ge 90.0\%$ | **97.5%** | Passed |
| **Recall** | $\frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$ | $\ge 85.0\%$ | **93.2%** | Passed |
| **F1-Score** | $\frac{2 \times \text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$ | $\ge 88.0\%$ | **95.3%** | Passed |
| **Near-Miss Discrimination** | $\frac{\text{Isolated Pairs}}{\text{Critical Near-Miss Pairs Tested}}$ | $\mathbf{100.0\%}$ | **100.0%** (0 false merges) | Passed |

### Near-Miss Discrimination Verification
- **6" CS Gate Valve 150# vs 6" CS Globe Valve 150#:** Score clamped to **0.14** $\rightarrow$ strictly isolated into separate clusters.
- **Deep Groove Ball Bearing 6205 vs Cylindrical Roller Bearing NJ 205:** Identical $25 \times 52 \times 15\text{ mm}$ envelope $\rightarrow$ strictly isolated.
- **Centrifugal End Suction Pump (40m head) vs Multistage Booster Pump (120m head):** Kept distinct.
- **Weld Neck Flange (WNRF) vs Slip-On Flange (SORF):** Kept distinct.

---

## 4. User Interface & Feature Tour

The web application is built with a modern **clean enterprise light theme** designed for procurement officers and material stewards:

1. **Executive Dashboard (`/`):** Real-time KPI summaries, CPSE system distribution, category breakdown, and live Defensible Ground-Truth Benchmark metrics.
2. **Candidate Review (`/matches`):** Two-pane master-detail workflow with confidence routing (HIGH / MEDIUM / LOW), transparent 3-signal progress breakdown, and Approve / Edit / Reject controls.
3. **National Material Master (`/catalog`):** Golden national catalog with full search, category filters, CSV export, and an interactive slide-over drawer proving 100% reverse traceability to constituent CPSE ERP items.
4. **Immutable Audit Trail (`/audit`):** Chronological event ledger with expandable side-by-side JSON diffs verifying state before vs state after mutation.

---

## 5. Technology Stack

- **Frontend:** React 18, Vite, Tailwind CSS, Lucide Icons (clean, high-contrast enterprise light theme).
- **Backend:** FastAPI (Python 3.12 modular monolith).
- **Database:** PostgreSQL 16 with `pgvector` (with automatic zero-config SQLite vector fallback for local evaluation).
- **AI & NLP:**
  - Sentence-Transformers (`all-MiniLM-L6-v2`, 384-dimensional dense vectors).
  - RapidFuzz (C++ accelerated token sort/set fuzzy matching).
  - Rule-based attribute extraction engine with Ollama Llama 3 endpoint integration.
- **Containerization:** Docker Compose (`db`, `backend`, `frontend`, `ollama`).

---

## 6. Quickstart Guide

### Option A: Run via Docker Compose (Single Command)
```bash
docker compose up --build
```
- Frontend UI: `http://localhost:3000`
- Backend Swagger Docs: `http://localhost:8000/docs`

---

### Option B: Run Locally

#### 1. Backend Setup
```bash
# From repository root
pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload --port 8000
```
*On initial startup, the backend automatically initializes database schema, seeds CPSE master data from `data/seed/cpse_seed.csv`, and executes the initial AI matching pipeline.*

#### 2. Frontend Setup
```bash
# In a separate terminal
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your web browser.

#### 3. Run Automated Tests
```bash
python -m pytest backend/tests/ -v
```
*Executes all 9 unit and integration tests (scoring formula, near-miss penalties, national code generator, human approval workflow, and precision/recall benchmarks).*

---

## 7. Project Structure

```
EkMat/
├── REAL_WORLD_IMPLEMENTATION_ROADMAP.md # Enterprise whitepaper & production scaling roadmap
├── README.md                            # Main project overview & quickstart
├── docker-compose.yml                   # 4-tier stack container orchestrator
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py                      # FastAPI entrypoint & auto-seeder
│   │   ├── core/                        # Config and vector-compatible database engine
│   │   ├── models/                      # SQLAlchemy models (CPSE, Material, Match, CommonMaterial, Audit)
│   │   ├── schemas/                     # Pydantic validation schemas
│   │   ├── services/                    # Preprocessing, Embeddings, RapidFuzz, Scoring, Clustering, CodeGen, Audit
│   │   └── api/                         # REST endpoints (Materials, Matches, CommonMaterials, Audit, Analytics)
│   └── tests/                           # Pytest suite with precision/recall benchmark
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── vite.config.js                   # Proxy configuration to backend on port 8000
│   └── src/
│       ├── App.jsx                      # Root container & tab routing
│       ├── api/client.js                # API fetch client
│       ├── components/                  # Navbar, KPICard, StatusBadge, ScoreBreakdown, Modals
│       └── pages/                       # Overview, MatchReview, MaterialMaster, AuditTrail
└── data/seed/
    ├── cpse_seed.csv                    # 186 synthetic CPSE materials across 52 clusters
    └── generate_dataset.py              # Seed generation script with ground truth labels
```

---

## 8. License

This project is licensed under the MIT License. Developed for Central Public Sector Enterprises Material Standardization and Harmonization.
