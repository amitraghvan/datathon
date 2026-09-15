# Phase 6: Graph-First AI Decision Intelligence Agent Architecture

## 1. Architectural Philosophy: The Anti-Hallucination Contract
The EduPulse AI Decision Intelligence Agent is **not** a generic conversational chatbot or wrapper around unconstrained LLMs. In public education administration, deploying open-ended text generators that invent formulas, fabricate statistics, or draft unparameterized SQL against production databases creates severe administrative and ethical liabilities.

EduPulse AI implements an enterprise-grade, **Graph-First Decision Intelligence Architecture**:
```
User Natural Language Query
           │
           ▼
[Security & Prompt Injection Guard] ──── Rejected ───> [Governance Advisory Notice]
           │ (Safe)
           ▼
[Session Memory & Context Injection] ──> Resolves deictic & multi-turn pronouns ("there", "its")
           │
           ▼
[Semantic Graph & Intent Classifier] ──> Classifies Intent (12 canonical types) & Resolves Entities
           │
           ▼
[Governed Metric Registry] ────────────> Resolves Canonical Metric Contracts, Sources, and Caveats
           │
           ▼
[Deterministic Query Planner] ─────────> Compiles Parametric SQL strictly over Approved Views
           │
           ▼
[SQL Safety Guard & AST Validator] ────> Enforces Read-Only SELECT/WITH; Blocks DDL/DML/System commands
           │
           ▼
[DuckDB Analytical Execution Engine] ──> Vectorized columnar execution (<30ms latency)
           │
           ▼
[Evidence Packager & Citation Engine] ──> Extracts records (N), coverage %, and generates verifiable citations
           │
           ▼
[Grounded Synthesis Engine] ───────────> Generates structured WHAT -> WHY -> EVIDENCE -> CAVEAT -> ACTION
           │
           ▼
[Anti-Hallucination Grounding Audit] ───> Validates claims against executed rows; flags causal phrasing
           │
           ▼
[Dynamic Visualization Planner] ───────> Recommends Bar, Horizontal Bar, Scatter, KPI, or Table
           │
           ▼
[Operational Action Recommender] ──────> Dispatches actionable policies from School 360 Catalog
           │
           ▼
Grounded Decision Intelligence Response (JSON / Interactive UI)
```

---

## 2. Core Architectural Subsystems

### 2.1 Security & Prompt Injection Guard (`src/agent/security/`)
- **Input Sanitization**: Strips non-printable ASCII control characters.
- **Buffer & DoS Protection**: Hard bounded query length at 1,500 characters.
- **Pattern Matching**: Regex-based detection blocking instruction hijacking (`ignore previous instructions`), developer-mode jailbreaks (`DAN`), system prompt exfiltration (`reveal system prompt`), raw SQL injection tokens (`UNION SELECT`, `DROP TABLE`), and script injection (`<script>`).
- **Deflection**: Generates a polite, deterministic security advisory notice without executing any SQL or warehouse queries.

### 2.2 Semantic Graph & Domain Ontology (`src/agent/graph/`)
- **Entity Resolution**: Identifies school identifiers (`SCH\d+`), 9 districts, 5 physical amenities, 4 welfare quadrants, commodities, and risk drivers.
- **12 Canonical Intent Types**: `LOOKUP`, `RANKING`, `COMPARISON`, `TREND`, `BREAKDOWN`, `DIAGNOSIS`, `ASSOCIATION`, `SEGMENTATION`, `ANOMALY`, `RECOMMENDATION`, `METHODOLOGY`, `DATA_QUALITY`.
- **Reasoning Lineage**: Formal graph paths detailing how conclusions are drawn (`intervention_diagnosis`, `district_welfare_audit`, `procurement_peer_exception`, `attendance_academic_association`).

### 2.3 Authoritative Metric Registry (`src/agent/graph/metric_registry.py`)
- Machine-readable catalog of 12 governed metrics:
  - `intervention_priority`: Composite 0-100 triage sequence.
  - `risk_score`: Absolute observable vulnerability index.
  - `attendance_rate_pct`: Weighted student attendance rate.
  - `academic_score`: FLN composite baseline.
  - `infrastructure_readiness_pct`: 3-valued physical amenity readiness.
  - `total_spend_inr`: Mid-Day Meal procurement expenditure.
  - `cost_variance_ratio`: 1.5 IQR peer distribution outlier indicator.
  - `attendance_academic_correlation`: Pearson $r = 0.453$ (observational only).
  - `data_trust_score`: 10-gate quality compliance score (94.6/100).
- **Non-Causal Governance**: Metrics flag causal claims as violations.

### 2.4 Deterministic Query Planner & SQL Builder (`src/agent/planner/`)
- Compiles validated intents into safe, parameterized SQL queries.
- Restricted strictly to three governed views:
  1. `school_master_enriched`
  2. `district_performance`
  3. `procurement_summary`
- View-specific filter pruning guarantees zero invalid column references.

### 2.5 Execution & AST Guard (`src/agent/execution/`)
- `SQLGuard`: Strictly validates that queries start with `SELECT` or `WITH`.
- Prohibits all mutating keywords (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`).
- Prohibits filesystem functions (`read_csv`, `read_parquet`, `read_json`, `httpfs`).
- Measures vectorized execution latency in milliseconds via `GovernedExecutor`.

### 2.6 Grounding, Anti-Hallucination & Citations (`src/agent/grounding/`)
- `package_evidence()`: Packages clean rows, sample sizes ($N$), and coverage metadata.
- `generate_citations()`: Generates verifiable citations detailing source view, record identifier, metric value, unit, and methodology reference.
- `validate_grounding()`: Audits every numeric claim in synthesized answers against the executed evidence records and whitelisted statistical constants.
- Flags causal phrasing (`causes`, `leads to`, `directly improves`) in observational analyses.

### 2.7 Synthesis & Recommendation Engine (`src/agent/synthesis/`)
- Implements standard consulting executive structure:
  - **WHAT**: High-level empirical finding.
  - **WHY**: Root cause drivers and comparative context.
  - **EVIDENCE**: Specific figures citing canonical DuckDB records.
  - **CAVEAT**: Observational vs causal boundaries, 3-valued logic, and sample coverage.
  - **ACTION**: Concrete operational next steps mapped to the School 360 Action Catalog.

### 2.8 Dynamic Visualization Planner (`src/agent/visualization/`)
- Automatically selects the optimal visualization format:
  - `bar`: Comparative district benchmarks.
  - `horizontal_bar`: Ranked queues and procurement outliers.
  - `scatter`: Bivariate associations (e.g. Attendance vs FLN score).
  - `kpi`: School 360 scorecards.
  - `table`: High-dimensional record matrices.

### 2.9 Multi-Turn Session Memory (`src/agent/memory/`)
- Bounded LRU session memory (default 10 turns).
- Tracks `last_district`, `last_school_id`, `last_metric`, and `last_intent_type`.
- Context resolution automatically binds pronouns ("there", "its", "that district") to the active entity.

---

## 3. End-to-End Latency Profile
Across all 52 benchmark evaluation queries:
- Intent Classification & Graph Lineage: **~0.5 ms**
- Parameterized Query Compilation: **~0.02 ms**
- DuckDB Columnar Execution: **18 - 28 ms**
- Evidence Packaging & Citations: **~0.1 ms**
- Grounding & Anti-Hallucination Audit: **~0.5 ms**
- **Total End-to-End Execution Latency**: **23.2 ms** (Average), **30.1 ms** (P95).
