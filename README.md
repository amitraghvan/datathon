# EduPulse AI — Education Welfare Command Center

> **Tagline:** *Clean. Connect. Detect. Explain. Act.*  
> **Track:** Track 4 — Education & EdTech Decision Intelligence  
> **Authoritative Data Trust Score:** **`94.6 / 100`** (Certified Analytics-Ready)  
> **Core Stack:** DuckDB 1.1+ • FastAPI • Next.js 16 (App Router) • Llama 3.1 • TailwindCSS v4 • Playwright  

---

## 1. Problem Statement
State education departments manage thousands of institutions, but operational data is trapped in fragmented, inconsistent formats: student attendance records contain duplicate entries and impossible boundaries; infrastructure reports contain missing values; assessment scores mix percentages with letter grades; and procurement spreadsheets record expenditures with arbitrary currency formatting and mismatched units. Without rigorous data rescue and governed analytics, education leaders make administrative interventions based on unverified, misleading indicators.

---

## 2. Solution Overview
**EduPulse AI** is a consulting-grade education decision intelligence platform. It ingests 44,928 raw records across five disparate state education datasets, applies a 10-gate deterministic cleaning pipeline to eliminate duplicates, normalizes multi-format dates, scales CBSE letter grades to mathematical midpoints, and compiles a canonical star-schema warehouse in **DuckDB**. 

Over this trusted foundation, EduPulse AI provides:
1. **Executive Command Center:** Real-time state-level KPIs, district rankings, and 2×2 Welfare Gap matrices.
2. **Intervention Command Center:** Operational prioritization distinguishing absolute **Risk Severity** (0–100) from administrative **Intervention Priority** (0–100).
3. **School 360:** Individual institutional diagnostics, statutory amenity checklists, attendance trends, and deterministic policy action protocols.
4. **Welfare & Infrastructure Intelligence:** Three-valued boolean tracking (`Available`, `Missing`, `Unknown`) across five physical amenities and observational electricity benchmarks.
5. **Mid-Day Meal Procurement:** Expenditure tracking, commodity volumes, and 1.5 IQR Peer Benchmark Exception audits.
6. **Data Trust Center:** End-to-end lineage contracts, dataset reconciliation matrices, and 10 quality gate audits.
7. **Graph-First AI Analyst:** Two-stage autonomous copilot utilizing Llama 3.1 for intent understanding and evidence synthesis while DuckDB remains the sole, authoritative source of truth.

---

## 3. Why the Raw Data Is Messy
The supplied dataset mirrors real-world administrative education data:
- **`track4_school_master.csv`**: Contains 18 duplicate entries, inconsistent ID formats (`sch_0386`, `SCH-0386`), and trailing whitespace.
- **`track4_student_attendance.csv`**: Contains 806 duplicate rows, mixed date formats (`DD/MM/YYYY`, `MM/DD/YYYY`, timestamps), and 214 records with negative student counts or present counts exceeding total enrollment.
- **`track4_school_infrastructure.csv`**: Contains 150 duplicate records and 382 ambiguous/null values (`?`, `na`, `null`), risking false assumptions of amenity absence.
- **`track4_mid_day_meal_procurement.xlsx`**: Formatted with currency strings (`₹ 1,20,500.00`, `INR`), mismatched unit scales (grams, quintals, bags), and 360 duplicate rows.
- **`track4_test_scores.json`**: Contains 1,542 records recorded as letter grades (`A`, `B`, `C`, `D`, `E`) alongside numerical scores.

---

## 4. System Architecture

```
                                  ┌───────────────────────────────┐
                                  │          Next.js UI           │
                                  │   (Executive Command Center)  │
                                  └───────────────┬───────────────┘
                                                  │ HTTP / JSON
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │          FastAPI API          │
                                  │     (Governed API Gateway)    │
                                  └───────────────┬───────────────┘
                                                  │
                 ┌────────────────────────────────┴────────────────────────────────┐
                 │                                                                 │
                 ▼                                                                 ▼
   ┌───────────────────────────┐                                     ┌───────────────────────────┐
   │    Analytics Services     │                                     │     AI Analyst Engine     │
   │ (Overview, Welfare, Risk) │                                     │  (Two-Stage Graph-First)  │
   └─────────────┬─────────────┘                                     └─────────────┬─────────────┘
                 │                                                                 │
                 │                                     ┌───────────────────────────┴───────────┐
                 │                                     ▼                                       ▼
                 │                              Semantic Graph                          Llama 3.1 LLM
                 │                         (Entity & Metric Registry)              (Language & Synthesis)
                 │                                     │                                       │
                 └─────────────────────────────────────┼───────────────────────────────────────┘
                                                       │ Governed SQL Queries
                                                       ▼
                                        ┌─────────────────────────────┐
                                        │       Governed DuckDB       │
                                        │    (10 Analytical Views)    │
                                        └──────────────┬──────────────┘
                                                       │
                                                       ▼
                                        ┌─────────────────────────────┐
                                        │   Canonical Parquet Marts   │
                                        │  (Star-Schema Fact Tables)  │
                                        └──────────────┬──────────────┘
                                                       │
                                                       ▼
                                        ┌─────────────────────────────┐
                                        │   Data Rescue & Ingestion   │
                                        │ (10 Quality Gates Pipeline) │
                                        └──────────────┬──────────────┘
                                                       │
                                                       ▼
                                        ┌─────────────────────────────┐
                                        │   Raw State Datasets (5)    │
                                        │ (CSV, XLSX, JSON Rescued)   │
                                        └─────────────────────────────┘
```

---

## 5. Data Rescue & Cleaning Proof

EduPulse AI executes a deterministic 10-gate quality pipeline (`docs/data_cleaning_report.md`):

| Dataset | Raw Records | Duplicates Removed | Rescued Records | Quarantined Records | Trusted Fact Rows | Referential Soundness |
|---|---|---|---|---|---|---|
| **School Master** | 618 | 18 | 0 | 0 | **600** (`dim_school`) | 100% Unique PKs |
| **Student Attendance** | 20,800 | 806 | 1,634 | 214 (bounds) | **19,994** (`fact_attendance`) | 0 Orphan School IDs |
| **School Infrastructure** | 3,150 | 150 | 382 (tri-state) | 0 | **3,000** (`fact_infrastructure`) | 0 Orphan School IDs |
| **MDM Procurement** | 12,360 | 360 | 1,302 (units/₹) | 0 | **12,000** (`fact_procurement`) | 0 Orphan School IDs |
| **FLN Test Scores** | 8,000 | 0 | 1,542 (grades) | 0 | **8,000** (`fact_assessment`) | 0 Orphan School IDs |
| **TOTALS** | **44,928** | **1,334** | **4,860** | **214** | **43,594** Fact Records | **0 Orphans (100%)** |

- **Quarantine Logic:** 214 attendance rows with mathematical boundary violations are tagged `quality_status = 'FLAGGED'` and quarantined without data loss.
- **Three-Valued Boolean Logic:** Preserves `TRUE`, `FALSE`, and `NULL` (UNKNOWN). Unverified amenities are never coerced to FALSE.
- **CBSE Midpoint Imputation:** $A \to 95.0$, $B \to 80.0$, $C \to 65.0$, $D \to 50.0$, $E \to 35.0$.

For full schemas, consult the [Canonical Data Dictionary](docs/data_dictionary.md).

---

## 6. Governed KPI Registry

Frontend views **never** compute authoritative metrics in React; all metrics originate from governed DuckDB SQL views (`docs/metric_audit.md`):

| Metric | Source View | Authoritative Formula | Cohort Value |
|---|---|---|---|
| **Schools Monitored** | `dim_school` | `COUNT(DISTINCT school_id)` | **600 institutions** |
| **Average Attendance** | `school_performance` | `SUM(present) * 100.0 / SUM(total)` | **79.4%** |
| **FLN Academic Score** | `school_performance` | `AVG(normalized_score)` | **66.2 / 100** |
| **Infrastructure Readiness** | `school_welfare` | `COUNT(available) * 100.0 / COUNT(reported)` | **74.8%** |
| **Priority Schools Queue** | `school_intervention_priority`| `COUNT(intervention_priority_score >= 35.0)` | **39 schools** |
| **High Priority Schools** | `school_intervention_priority`| `COUNT(intervention_priority_score >= 45.0)` | **15 schools** |
| **Critical Risk Severity** | `school_risk` | `COUNT(risk_score >= 70.0)` | **0 schools** |
| **Master Data Trust Score** | `school_data_quality` | 10-Gate Weighted Index | **94.6 / 100** |
| **MDM Gross Expenditure** | `fact_procurement` | `SUM(total_cost)` | **₹6,438,710.00** |
| **MDM Gross Food Volume** | `fact_procurement` | `SUM(quantity_kg)` | **146,825 kg** |
| **Peer Benchmark Exceptions** | `procurement_anomalies` | `Cost/Pupil > 75th pctl + 1.5 IQR` | **18 schools** |
| **Attendance-FLN Correlation** | `school_performance` | Pearson correlation coefficient ($r$) | **0.453** (Observational) |

---

## 7. Analytical Rigor: Risk Severity vs. Intervention Priority

A critical contribution of EduPulse AI is the operational distinction between **Risk Severity** and **Intervention Priority**:

1. **Risk Severity Score (0–100):** Objective magnitude of observed vulnerabilities across attendance deficits (40%), academic deficits (35%), and infrastructure deficits (25%).  
   *Observed State Result:* 0 schools exceed the $\ge 70.0$ critical severity threshold; the cohort exhibits moderate vulnerabilities.
2. **Intervention Priority Score (0–100):** Administrative scheduling priority for resource allocation, incorporating district-relative deficits, confidence adjustments, and multi-factor flags:  
   $$\text{Priority} = \min(100.0, (\text{Risk} \times 0.60) + \min(30.0, \text{DistrictDeficit}) \times 0.67 + \text{MultiFactorBoost} + \text{ConfidenceBoost})$$  
   *Observed State Result:* **39 schools** require targeted intervention review ($\ge 35.0$).

> [!NOTE]
> **39 Priority Schools and 0 Critical Risk Severity is NOT a contradiction.**  
> While no school is in catastrophic absolute collapse, 39 schools have urgent relative deficits compared to their peers that demand immediate administrative action.

---

## 8. Dashboard Modules

- **`/` — Executive Command Center:** Briefing dashboard with 6 KPIs, dynamic insight banners, district rankings, 2×2 Welfare Gap scatter matrix, attendance-academic correlation, and single compact filter row.
- **`/schools` — School Directory:** Searchable catalog with district, block, medium, and type filters.
- **`/schools/[id]` — School 360:** Individual diagnostic profile featuring 5 amenity checklists, historical attendance trends, FLN subject breakdown, and deterministic policy actions.
- **`/welfare` — Welfare & Infrastructure:** 5 physical amenities tracking and competition electricity vs FLN score benchmark.
- **`/procurement` — Mid-Day Meals:** Expenditure distribution, commodity volume breakdown, and 18 Peer Benchmark Exceptions.
- **`/intervention` — Intervention Command Center:** Priority queue table, driver taxonomy, risk vs priority scatter, and sensitivity proofs.
- **`/quality` — Data Trust Center:** Master Trust Score (94.6/100), 10 Quality Gates checklist, and end-to-end KPI lineage.
- **`/ai-analyst` — AI Analyst Workbench:** Natural language decision intelligence with automatic chart selection, SQL compilation, citations, and claim validation.

---

## 9. Graph-First AI Analyst & Llama 3.1 Governance

The AI Analyst (`src/agent/`) implements an explicit two-stage architecture:

1. **Stage 1 (Intent & Entity Resolution):** Llama 3.1 translates natural language into a typed `AgentIntent` validated against Pydantic schemas and the semantic metric registry.
2. **Deterministic Planner:** Compiles parameterized, read-only SQL queries executed directly against DuckDB.
3. **Stage 2 (Answer Synthesis):** Llama 3.1 synthesizes the narrative strictly from verified DuckDB evidence records.
4. **Claim Validator:** Audits every number, school ID, and district name against the executed records; detects and rejects unsupported causal verbs (*"causes"*, *"proves"*).
5. **Circuit Breaker:** Automatically routes to the zero-latency deterministic engine on LLM provider rate limits (Groq 429) or timeouts, returning HTTP 200 with `status: "degraded"`.
6. **Fast-Path Greeting:** Recognizes casual inputs (*"hi"*, *"hello"*) in **0.06 ms** with zero database calls.

### Text-to-Chart Automatic Selection Policy
- **Ranking** -> `horizontal_bar`
- **District Comparison** -> `bar`
- **Statistical Association** -> `scatter`
- **Root-Cause Diagnosis** -> `kpi` / `table`
- **Welfare Quadrants** -> `scatter` matrix
- **Exceptions & Anomalies** -> `table`

---

## 10. Top 5 Hackathon Demo Prompts

Try these verified prompts in `/ai-analyst`:

1. **Prompt 1 (Priority Triage):**  
   *"Which 10 schools should be reviewed first?"*  
   *Result:* Returns top 10 queue institutions led by SCH0386 (Priority 54.2) with a horizontal bar chart.
2. **Prompt 2 (Root-Cause Diagnosis):**  
   *"Why is SCH0386 in the intervention queue?"*  
   *Result:* Diagnoses infrastructure constraint (60.0%), FLN score (64.8%), and attendance (79.1%).
3. **Prompt 3 (Infrastructure Deficit):**  
   *"Which districts have the weakest infrastructure?"*  
   *Result:* Identifies Ferozepur (70.6%) and Fazilka (71.2%) with a horizontal bar chart.
4. **Prompt 4 (Statistical Association):**  
   *"Are attendance and academic scores associated?"*  
   *Result:* Returns Pearson $r = 0.453$ with a scatter chart and explicit non-causal disclaimer.
5. **Prompt 5 (Peer Benchmark Exceptions):**  
   *"Which procurement records are peer benchmark exceptions?"*  
   *Result:* Displays 18 statistical spend-per-student outlier schools with operational context.

---

## 11. Frontend Architecture & Enterprise Design System

The EduPulse AI frontend has been engineered from the ground up into a **pure white, minimal, institutional, consulting-grade decision intelligence platform** modeled after executive briefing artifacts prepared by Tier-1 strategy consultancies (McKinsey, BCG, Deloitte) and government data portals.

### Core Visual Principles
- **Crisp Light Canvas:** Pure white card surfaces (`#FFFFFF`) on a subtle light slate canvas (`#F8FAFC`) with restrained hairline borders (`#E2E8F0`). Zero neon glows, zero dark-admin clutter, zero arbitrary decorative cards.
- **Consulting-Grade Typography:** Clean, modern enterprise hierarchy utilizing system sans-serif typography (`Inter`, `-apple-system`) with AAA contrast (16.1:1 on primary text `#0F172A`).
- **Tri-State Transparency:** Physical amenities strictly differentiate **Available** (Emerald `#059669`), **Missing** (Rose `#DC2626`), and **Unknown / Unverified** (Neutral Slate `#64748B`), eliminating false assumptions of absence.
- **Analytical Governance:** Strict visual and conceptual separation between **Risk Severity** (observed historical vulnerability magnitude) and **Intervention Priority** (administrative review urgency).

### Page-by-Page Decision Routing
| Route | Page Name | Primary Leadership Question Answered | Key Visual Components |
|---|---|---|---|
| `/` | **Executive Command Center** | *"What is the statewide operational health and where should leadership look first?"* | MetricCard Big Numbers, Strategic Policy Dispatch, District FLN Ranking Bar, Welfare Gap Scatter, Top 10 Priority Table |
| `/schools` | **School Directory & Search** | *"How can I locate and inspect any specific institution across the 600-school census?"* | Real-time UDISE search bar, district filter, sortable metrics, School 360 profile launch |
| `/schools/[id]` | **School 360 Diagnostic Profile** | *"What is the comprehensive institutional root-cause diagnosis and mandated policy action for this school?"* | Statutory 5-amenity checklist, attendance timeseries chart, FLN subject breakdown, MDM procurement summary, deterministic policy action memo |
| `/welfare` | **Welfare & Infrastructure** | *"Which physical amenities are deficient and how do they correlate with learning efficacy?"* | 5 core amenity penetration cards with Available/Missing/Unknown counters, Electricity vs FLN observational benchmark, Welfare Gap Matrix |
| `/procurement` | **Mid-Day Meals & Nutrition** | *"How are public nutrition funds allocated and which schools deviate from peer spend patterns?"* | Spend and grain volume metric cards, district spend bar chart, 1.5 IQR peer benchmark exception audit table |
| `/intervention` | **Intervention Command Center** | *"Which schools require immediate administrative intervention and what is driving their vulnerability?"* | Risk Severity vs Intervention Priority Matrix, driver taxonomy cards, full 50-institution priority queue table |
| `/quality` | **Data Trust & Governance** | *"Can decision-makers trust this underlying data?"* | 94.6/100 Data Trust Score, 5-stage automated rescue pipeline visual, 10 Quality Gates audit, KPI lineage catalog |
| `/ai-analyst` | **AI Decision Analyst Workbench** | *"Can leadership ask natural-language policy questions grounded solely in verified facts?"* | Natural language inquiry input, curated showcase missions, animated reasoning stepper, structured evidence memo, grounding audit, verifiable citations |

---

## 12. Project Structure

```
DATATHON/
├── backend/                  # FastAPI Backend Application
│   ├── app/
│   │   ├── api/v1/           # Modular API route controllers
│   │   ├── repository/       # DuckDB connection pool & queries
│   │   ├── schemas/          # Typed Pydantic v2 data models
│   │   ├── services/         # Governed business analytics services
│   │   └── main.py           # Application entrypoint & middleware
│   └── tests/                # API integration & security tests
├── data/
│   ├── processed/            # Canonical Parquet marts & edupulse.duckdb
│   └── raw/                  # Original uncleaned state files
├── docs/                     # Comprehensive Architecture & Audit Reports
│   ├── data_dictionary.md    # Canonical table schemas & null semantics
│   ├── data_cleaning_report.md# Raw-to-clean reconciliation proof
│   ├── system_architecture.md# Technical architecture & data flows
│   ├── ai_architecture.md    # Semantic graph & grounding engine
│   ├── metric_audit.md       # 24 governed metrics audit matrix
│   ├── final_audit_report.md # Production readiness audit (A–K)
│   ├── ui_bug_audit.md       # Visual inspection & defect resolutions
│   └── demo_script.md        # 3-minute presenter script for judges
├── evaluation/               # Agent evaluation test harness
│   ├── agent_eval_set.json   # 52 benchmark test queries
│   └── evaluate_agent.py     # Automated benchmark scoring script
├── frontend/                 # Next.js 16 Executive Web Application
│   ├── app/                  # App Router pages (/schools, /welfare, /ai-analyst)
│   ├── components/           # Reusable UI cards, tables, charts, skeletons
│   ├── e2e/                  # Playwright end-to-end user journeys
│   └── lib/                  # API client, TypeScript types, formatters
├── src/                      # Core ETL & AI Agent Engine
│   ├── agent/                # Graph-first AI agent orchestrator
│   │   ├── execution/        # Governed SQL executor & guardrails
│   │   ├── graph/            # Semantic graph & metric registry
│   │   ├── grounding/        # Claim validator & citations
│   │   └── llm/              # Llama 3.1 & MockDeterministic providers
│   └── pipeline.py           # 10-gate data rescue pipeline
└── Makefile                  # One-click operational commands
```

---

## 13. Installation & Local Development

### Prerequisites
- Python 3.11+ (Tested on Python 3.13.7)
- Node.js 18+ (Tested on Node.js v20+)
- npm or yarn

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/your-org/edupulse-ai.git
cd edupulse-ai

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install && cd ..
```

### 2. Environment Variables Configuration
Copy `.env.example` to `.env` in the root directory:
```bash
cp .env.example .env
```

Key environment variables:
```ini
# Warehouse Path
DUCKDB_DATABASE_PATH=data/processed/edupulse.duckdb

# LLM Configuration (Llama 3.1 via Groq or OpenAI-compatible)
LLAMA_API_KEY=gsk_your_groq_api_key_here
LLAMA_BASE_URL=https://api.groq.com/openai/v1
LLAMA_MODEL=qwen/qwen3.8-27b

# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```
*(Note: If no LLM credentials are provided, EduPulse AI runs automatically in zero-latency deterministic mode with full functionality.)*

### 3. Build Canonical Warehouse (Reproducible Pipeline)
```bash
# Re-run 10-gate rescue pipeline and compile DuckDB database
make pipeline
# OR
python -m src.pipeline
```

### 4. Run Servers Locally
Open two terminal windows:

**Terminal 1 — Backend (FastAPI):**
```bash
source .venv/bin/activate
uvicorn backend.app.main:app --port 8000 --host 127.0.0.1
```
*API docs available at:* `http://localhost:8000/docs`

**Terminal 2 — Frontend (Next.js):**
```bash
cd frontend
npm run dev
```
*Web dashboard available at:* `http://localhost:3000`

---

## 14. Test Suite Verification

EduPulse AI includes a comprehensive test suite covering backend logic, security constraints, frontend components, and end-to-end browser user journeys:

```bash
# 1. Run all 191 Python tests (unit, integration, SQL guard, prompt injection)
pytest tests/ backend/tests/ -v

# 2. Run 52-question AI Agent evaluation benchmark
python evaluation/evaluate_agent.py

# 3. Run frontend unit tests (Vitest)
cd frontend && npm test && cd ..

# 4. Run frontend TypeScript & ESLint verification
cd frontend && npx tsc --noEmit && npm run lint && cd ..

# 5. Run Playwright E2E browser tests (All 4 user journeys)
cd frontend && npx playwright test && cd ..
```

---

## 15. Live Deployment Readiness

EduPulse AI is architected for containerized or serverless cloud deployment:

- **Backend:** Deployable to AWS ECS, Google Cloud Run, or Railway (`uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`).
- **Frontend:** Deployable to Vercel or Netlify with `NEXT_PUBLIC_API_BASE_URL` pointing to the live API gateway.
- **Warehouse:** The compiled `data/processed/edupulse.duckdb` file (14.6 MB) is bundled with the backend container for zero-latency in-process querying.

---

## 16. Responsible Interpretation & Governance Disclaimers

1. **Non-Causal Classification:** All bivariate associations (such as attendance vs FLN academic performance, $r = 0.453$) are observational. Observed performance differences across infrastructure amenities do not prove causality without controlled trials.
2. **Peer Benchmark Exceptions:** Spend-per-student anomalies exceeding 75th percentile + 1.5 IQR thresholds identify observations that differ materially from comparable peer patterns; they do **not** represent evidence of fraud without forensic audit proof.
3. **Tri-State Transparency:** Amenities with unverified data are preserved as `UNKNOWN` and never assumed to be absent.

---

## 17. Presentation & Demo Walkthrough
For the live 3-minute hackathon judge walkthrough, refer to the [3-Minute Demo Script](docs/demo_script.md).

---

## 18. License
Licensed under the Apache 2.0 License. Built for Track 4: Education & EdTech Datathon 2026.
