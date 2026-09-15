# EDUPULSE AI — End-to-End Enterprise Architecture
## Track 4: Education & EdTech — Student Retention & Welfare Efficacy Tracker

---

## 1. System Architecture Overview

**EDUPULSE AI** follows a multi-tiered, decoupled analytics engineering architecture designed for data trust, mathematical rigor, and lightning-fast analytical queries:

```mermaid
flowchart TD
    subgraph Raw Layer
        R1[track4_school_master.csv]
        R2[track4_student_attendance.csv]
        R3[track4_school_infrastructure.csv]
        R4[track4_mid_day_meal_procurement.xlsx]
        R5[track4_test_scores.json]
    end

    subgraph Data Rescue & Cleansing (src/cleaning/)
        C1[School ID Canonicalizer]
        C2[Multi-Pattern Date Parser]
        C3[Boolean & Amenity Normalizer]
        C4[Unit Standardizer & Price Derivation]
        C5[FLN Score Standardizer & Proxy Mapper]
        C6[District Hierarchy Imputation]
        C7[Deduplication Engine]
    end

    subgraph Analytical Storage Layer (data/processed/)
        P1[(schools_clean.parquet)]
        P2[(attendance_clean.parquet)]
        P3[(infrastructure_clean.parquet)]
        P4[(procurement_clean.parquet)]
        P5[(assessments_clean.parquet)]
        A1[(cleaning_audit.parquet)]
    end

    subgraph DuckDB Analytical Warehouse (edupulse.duckdb)
        subgraph Star Schema Dimensions
            D1[(dim_school)]
            D2[(dim_date)]
            D3[(dim_grade)]
            D4[(dim_subject)]
            D5[(dim_vendor)]
            D6[(dim_grain)]
        end

        subgraph Star Schema Facts
            F1[(fact_attendance)]
            F2[(fact_assessment)]
            F3[(fact_infrastructure)]
            F4[(fact_procurement)]
        end

        subgraph Governed SQL Views
            V1{{school_performance}}
            V2{{school_welfare}}
            V3{{district_performance}}
            V4{{procurement_summary}}
            V5{{school_data_quality}}
            V6{{school_risk}}
            V7{{school_intervention_priority}}
            V8{{school_welfare_gap}}
            V9{{district_risk_summary}}
            V10{{procurement_anomalies}}
        end
    end

    subgraph Phase 4 Analytics & Risk Engine (src/analytics/)
        A1_R[Risk Engine - 45% Att / 35% Acad / 20% Infra]
        A2_W[Welfare Gap Matrix - 2x2 Model/Resilient]
        A3_K[School Segmentation - K-Means K=4]
        A4_S[Sensitivity Engine - Weights & Proxies]
    end

    subgraph Consumption Layer (Future Phases)
        UI[Streamlit Executive Command Center]
        AI[Graph-First Decision Agent]
    end

    R1 --> C1 & C6 & C7
    R2 --> C1 & C2 & C7
    R3 --> C1 & C2 & C3 & C7
    R4 --> C1 & C2 & C4 & C7
    R5 --> C1 & C2 & C5

    C1 & C2 & C3 & C4 & C5 & C6 & C7 --> P1 & P2 & P3 & P4 & P5 & A1

    P1 & P2 & P3 & P4 & P5 --> D1 & D2 & D3 & D4 & D5 & D6
    P1 & P2 & P3 & P4 & P5 --> F1 & F2 & F3 & F4

    D1 & D2 & D3 & D4 & D5 & D6 --> V1 & V2 & V3 & V4 & V5 & V6 & V7 & V8 & V9 & V10
    F1 & F2 & F3 & F4 --> V1 & V2 & V3 & V4 & V5 & V6 & V7 & V8 & V9 & V10

    V1 & V2 & V3 & V4 & V5 & V6 & V7 & V8 & V9 & V10 --> A1_R & A2_W & A3_K & A4_S
    A1_R & A2_W & A3_K & A4_S --> UI & AI
```

---

## 2. Table Specifications & Dimensional Grain

### Dimensions

| Table Name | Primary Key | Business Key | Row Count | Ingestion Source |
| :--- | :--- | :--- | :--- | :--- |
| **`dim_school`** | `school_key` (INT) | `school_id` (`SCHxxxx`) | 600 | `schools_clean.parquet` |
| **`dim_date`** | `date_key` (YYYYMMDD) | `date` (DATE) | 365 | Distinct dates across all fact tables |
| **`dim_grade`** | `grade_key` (INT) | `grade_number` (1–10) | 10 | Derived from attendance & assessments |
| **`dim_subject`** | `subject_key` (INT) | `subject_standard` | 6 | Distinct FLN assessment subjects |
| **`dim_vendor`** | `vendor_key` (INT) | `vendor_id` (`VENxxx`) | 4 | Resolved vendor entities from procurement |
| **`dim_grain`** | `grain_key` (INT) | `grain_standard` | 4 | Canonical MDM commodities |

### Facts

| Table Name | Primary Key | Foreign Keys | Row Count | Granularity |
| :--- | :--- | :--- | :--- | :--- |
| **`fact_attendance`** | `record_key` (INT) | `school_key`, `date_key`, `grade_key` | 19,994 | Daily attendance report per grade per school |
| **`fact_assessment`** | `assessment_key` (INT) | `school_key`, `date_key`, `grade_key`, `subject_key` | 8,000 | Assessment administration per grade per school |
| **`fact_infrastructure`** | `inspection_key` (INT) | `school_key`, `date_key` | 3,000 | Inspection event per school |
| **`fact_procurement`** | `procurement_key` (INT) | `school_key`, `date_key`, `vendor_key`, `grain_key` | 12,000 | Procurement transaction invoice per school |

---

## 3. Governed Analytical Views

1. **`school_performance`**:
   - Computes weighted attendance rate: $\frac{\sum \text{present}}{\sum \text{total}} \times 100$ on trusted records.
   - Computes weighted academic score: $\frac{\sum (\text{score} \times \text{assessed})}{\sum \text{assessed}}$.
   - Reports attendance and assessment coverage metrics.
2. **`school_welfare`**:
   - Distinguishes confirmed functional amenities ($1.0$), confirmed broken ($0.0$), and uninspected ($0.5$).
   - Calculates the composite Infrastructure Readiness Index ($0 - 100\%$).
3. **`district_performance`**:
   - District-level aggregation of attendance, academics, infrastructure, and high-quality school counts.
4. **`procurement_summary`**:
   - Aggregates expenditure, commodity volume, cost per student, and cost per kg with safe division by zero.
5. **`school_data_quality`**:
   - Multi-domain trust matrix tracking trusted, flagged, and excluded records per school.
6. **`school_risk`**:
   - Computes attendance risk (45%), academic risk (35%), infrastructure risk (20%), composite risk score, and risk bands.
7. **`school_intervention_priority`**:
   - Synthesizes risk severity (60%), district deficit penalty (20%), multi-factor vulnerability (10%), and coverage confidence (10%) into deterministic intervention ranking.
8. **`school_welfare_gap`**:
   - Classifies schools into 2x2 matrix: Model, Resilient, Academic Intervention, Critical Intervention.
9. **`district_risk_summary`**:
   - High-level leadership intelligence for cross-district intervention allocation.
10. **`procurement_anomalies`**:
    - Flags spend per student and commodity mix outliers using peer IQR benchmarks.

---

## 4. Query Performance & Storage Strategy

- **Dual-Engine Model**:
  - **Parquet**: Immutable, columnar, compressed analytical layer for long-term auditability and portable distribution.
  - **DuckDB**: In-process, vectorized SQL query engine executing analytical views and ad-hoc aggregations in sub-second runtimes ($< 200\text{ms}$).

---

## 5. Phase 4 Analytics & Risk Engine

- **`src/analytics/risk.py`**: Multi-factor Retention Risk Proxy and Intervention Priority scoring engine with dynamic weight re-normalization.
- **`src/analytics/advanced.py`**: Parametric/non-parametric association analysis (strictly non-causal), 2x2 Welfare Gap Matrix, policy weight sensitivity, letter-grade proxy robustness, and procurement IQR outlier detection.
- **`src/analytics/segmentation.py`**: Unsupervised K-Means clustering ($K=4$, $\text{Silhouette}=0.216$) with interpretable educational profile labeling.
- **`src/analytics/pipeline.py`**: Analytical mart materializer exporting Parquet datasets and DuckDB tables.

