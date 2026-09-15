# System Architecture — EduPulse AI Platform

**Platform:** EduPulse AI — Education Welfare Command Center  
**Tagline:** Clean. Connect. Detect. Explain. Act.  
**Architecture Paradigm:** Governed Decoupled Stack (DuckDB Analytical Warehouse + FastAPI Governed Services + Next.js Executive UI + Graph-First AI Agent)

---

## 1. Golden Architecture Flow

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

## 2. Core Architectural Pillars

### Pillar 1: Non-Negotiable Source of Truth (DuckDB)
- **DuckDB 1.1+** operates as the single authoritative repository of truth.
- The Frontend **never** calculates authoritative aggregations or policy formulas.
- The LLM **never** serves as the source of truth; it is structurally incapable of altering warehouse state or fabricating authoritative metrics.

### Pillar 2: Governed Two-Stage AI Reasoning
1. **Stage 1 (Intent & Entity Resolution):** The user prompt is mapped into a strict, validated `AgentIntent` via the domain ontology and semantic graph.
2. **Stage 2 (Grounded Execution & Synthesis):** The query planner compiles a safe, parameterized SQL query executed directly against DuckDB. The returned evidence records are passed to the synthesizer with mandatory citations, caveats, and claim validation.

### Pillar 3: Three-Valued Logic & Non-Causal Governance
- **Tri-State Infrastructure:** Physical amenities are stored as `TRUE` (Available), `FALSE` (Missing), and `NULL` (UNKNOWN). UNKNOWN is never coerced to FALSE.
- **Observational Integrity:** Statistical relationships (such as attendance vs FLN score, $r = 0.453$) are explicitly governed as observational. Causal claims are rejected by the claim validator.
- **Neutral Procurement Terminology:** Outliers exceeding the 75th percentile + 1.5 IQR peer spend threshold are formally designated as **"Peer Benchmark Exceptions"**, accompanied by statutory non-fraud disclaimers.

---

## 3. Technology Stack

| Layer | Technology | Primary Role |
|---|---|---|
| **Data Warehouse** | DuckDB 1.1+ Columnar | High-performance in-memory analytical SQL processing |
| **Storage Marts** | Apache Parquet | Snappy-compressed canonical star-schema columnar marts |
| **Pipeline Engine** | Python 3.13, Pandas, PyArrow | Data rescue, 10 quality gates, CBSE scaling, reconciliation |
| **Backend API** | FastAPI, Pydantic v2, Uvicorn | Governed REST endpoints, typed contracts, rate-limit fallback |
| **AI Analyst** | Llama 3.1 (Groq API) / Qwen / Deterministic Engine | Two-stage structured planning, natural language synthesis |
| **Frontend UI** | Next.js 16 (App Router), React 19, TypeScript | Executive command center, responsive consulting design system |
| **Styling & Icons**| TailwindCSS v4, Lucide React | Executive dark-mode palette, accessible WCAG contrast |
| **Visualizations** | Recharts v2.15 | Interactive charts (Bar, Horizontal Bar, Scatter, Line, Matrix) |
| **Client State** | TanStack React Query v5 | 5-minute caching, automatic request deduplication |
| **E2E Testing** | Playwright Chromium | Automated critical user journey validation |
