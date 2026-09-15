# Architecture Freeze Note: Phase 5 Decoupled Enterprise Platform

**Document Version**: 1.0.0  
**Project**: EduPulse AI — Education Welfare Command Center  
**Status**: ARCHITECTURE FROZEN  
**Date**: 2026-09-11  

---

## 1. Executive Summary & Strategic Pivot

Per Phase 5 requirements, EduPulse AI has transitioned from a monolithic prototype (Streamlit) to an enterprise-grade, consulting-style decoupled architecture:
- **Presentation Layer**: Next.js 14/15 (App Router), TypeScript (Strict Mode), Tailwind CSS, Lucide React, Recharts / Plotly, TanStack Query, and Zod.
- **Governed API Layer**: Python FastAPI (v0.141+), Pydantic v2, Uvicorn.
- **Analytical & Warehouse Core**: Embedded DuckDB (v1.5+), Governed SQL Views, and Canonical Parquet Data Marts.

---

## 2. Core Separation of Concerns & Non-Negotiable Rules

```
                 ┌──────────────────────────────────────┐
                 │       NEXT.JS (APP ROUTER)           │
                 │   Presentation & Interactive UI      │
                 └──────────────────┬───────────────────┘
                                    │
                                HTTPS JSON
                          (/api/v1/* contracts)
                                    │
                 ┌──────────────────▼───────────────────┐
                 │          FASTAPI BACKEND             │
                 │  Input Validation & Service Facade   │
                 └──────────────────┬───────────────────┘
                                    │
                 ┌──────────────────▼───────────────────┐
                 │      DUCKDB VECTORIZED ENGINE        │
                 │ Governed SQL Views & Star-Schema     │
                 └──────────────────┬───────────────────┘
                                    │
                 ┌──────────────────▼───────────────────┐
                 │ CANONICAL DATA MARTS / PARQUET FILES │
                 │ 6 Dimensions · 4 Facts · 10 Views    │
                 └──────────────────────────────────────┘
```

### Non-Negotiable Architectural Rules:
1. **Python / DuckDB is the Single Analytical Source of Truth**:
   The frontend must **NEVER** calculate attendance rates, academic scores, risk severity, intervention priorities, infrastructure indices, or IQR outlier bounds. All statistical aggregations and thresholds originate from compiled SQL views and analytical modules in `src/modeling/` and `src/analytics/`.
2. **Frontend Ingestion Boundary**:
   The frontend must **NEVER** read raw CSVs, raw Excel files, raw JSON, or access DuckDB directly. It exclusively communicates via REST JSON endpoints at `/api/v1/*`.
3. **Strict Metric Separation**:
   - **Risk Score (0–100)**: Quantifies observed vulnerability severity based on weighted deficits (Attendance 45%, Academic FLN 35%, Infrastructure 20%).
   - **Intervention Priority (0–100)**: Quantifies administrative urgency and review sequence, combining risk severity with district relative gaps and multi-factor flags.
   - The UI must never display "0 Critical Schools = No Problem" when schools require priority review.
4. **Three-Valued Infrastructure Logic**:
   The 5 core amenities (`electricity`, `drinking_water`, `functional_toilet`, `boundary_wall`, `playground`) must strictly support `TRUE`, `FALSE`, and `UNKNOWN`. Under no circumstances may `UNKNOWN` be coerced to `FALSE`.
5. **Observational & Non-Causal Governance**:
   All attendance-academic correlations ($r = 0.453$) and electricity comparisons must prominently state: *"This comparison describes observed differences; it does not establish causation."*
6. **Neutral Procurement Outlier Framing**:
   Outliers identified via 1.5 IQR peer spend thresholds must be designated as *"Peer Benchmark Exceptions"* and contextualized by delivery batch sizes or commodity mix, never branded as "fraud".
7. **Phase 6 AI Agent Decoupling**:
   FastAPI exposes a contract placeholder at `/api/v1/agent/query`, but no LLM agent or autonomous action loop will be introduced until Phase 6.

---

## 3. Verified Baseline

- **Unit & Regression Tests**: 124/124 tests passing (`pytest tests/`).
- **Data Pipelines**: Pipeline execution completed with 94.6/100 Data Trust Score.
- **DuckDB Marts**: `edupulse.duckdb` built with 6 dimensions, 4 facts, and 10 analytical views.
- **Parquet Outputs**: All 6 governed marts validated and materialized.
