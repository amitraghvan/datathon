# Canonical Data Dictionary — EduPulse AI Warehouse

**Platform:** EduPulse AI — Education Welfare Command Center  
**Warehouse Engine:** DuckDB 1.1+ Columnar Analytical Engine (`data/processed/edupulse.duckdb`)  
**Data Model:** Star Schema with Pre-Aggregated Analytical Marts  
**Authoritative Status:** 24 Governed KPIs • 0 Foreign Key Orphans • 10 Quality Gates  

---

## 1. Dimensional Tables

### 1.1 `dim_school` (School Dimension)
- **Granularity:** 1 row per canonical educational institution
- **Row Count:** 600 unique institutions
- **Primary Key:** `school_id`

| Column Name | Data Type | Null Semantics | Allowed Values / Range | Business Definition & Transformation | Analytical Role |
|---|---|---|---|---|---|
| `school_id` | `VARCHAR` | Non-Null | `SCH` + 4 digits (`SCH0001`–`SCH0600`) | Standardized 7-character canonical school identifier; regex-validated | Primary Key, Entity Join Key |
| `school_name` | `VARCHAR` | Non-Null | String (e.g., "Govt. Sen. Sec. School") | Rescued institutional name with casing and whitespace normalized | Display & Title |
| `district` | `VARCHAR` | Non-Null | 9 Punjab Districts: Amritsar, Bathinda, Ferozepur, Gurdaspur, Hoshiarpur, Jalandhar, Ludhiana, Moga, Patiala | Administrative district governing school operations | Primary Slice Dimension |
| `block` | `VARCHAR` | Non-Null | 23 Administrative Sub-District Blocks | Sub-district administrative block | Sub-District Drilldown |
| `school_type` | `VARCHAR` | Non-Null | `Primary`, `Middle`, `High`, `Senior Secondary` | Categorical operational grade span of institution | Cohort Segmentation |
| `medium` | `VARCHAR` | Non-Null | `Punjabi`, `English`, `Hindi` | Primary medium of instruction | Language Policy Analysis |
| `total_enrolled_students`| `INTEGER` | Non-Null | 50 to 500 pupils | Official enrolled pupil population from School Master | Normalization Denominator |

---

### 1.2 `dim_date` (Temporal Dimension)
- **Granularity:** 1 row per calendar day
- **Row Count:** 365 days (Full Academic Year)
- **Primary Key:** `date_key`

| Column Name | Data Type | Null Semantics | Range | Transformation & Definition |
|---|---|---|---|---|
| `date_key` | `INTEGER` | Non-Null | `YYYYMMDD` (e.g., 20240401) | Integer surrogate key for high-performance join scanning |
| `date` | `DATE` | Non-Null | `2024-04-01` to `2025-03-31` | ISO-8601 standardized calendar date |
| `academic_quarter` | `VARCHAR` | Non-Null | `Q1`, `Q2`, `Q3`, `Q4` | Academic reporting period |
| `is_school_day` | `BOOLEAN` | Non-Null | `TRUE`, `FALSE` | Operational school calendar indicator |

---

### 1.3 `dim_grain` (Commodity Dimension)
- **Granularity:** 1 row per Mid-Day Meal food grain type
- **Row Count:** 4 items (`Wheat`, `Rice`, `Pulses`, `Cooking Oil`)

| Column Name | Data Type | Units | Benchmark Statutory Price | Transformation & Role |
|---|---|---|---|---|
| `grain_key` | `INTEGER` | N/A | 1 to 4 | Commodity surrogate key |
| `grain_standard` | `VARCHAR` | N/A | Standardized Name | Canonical commodity label |
| `statutory_rate_inr_kg` | `DOUBLE` | INR / KG | Wheat: ₹30, Rice: ₹40, Oil: ₹120 | Official state benchmark schedule for peer exception testing |

---

## 2. Fact Tables

### 2.1 `fact_attendance` (Student Attendance Fact)
- **Granularity:** 1 row per school per attendance recording session
- **Row Count:** 19,994 operational rows
- **Foreign Keys:** `school_id` -> `dim_school.school_id`, `date_key` -> `dim_date.date_key`

| Column Name | Data Type | Null Semantics | Range | Transformation & Quality Logic |
|---|---|---|---|---|
| `attendance_id` | `VARCHAR` | Non-Null | Hash / UUID | Composite grain identifier |
| `school_id` | `VARCHAR` | Non-Null | Valid `dim_school` FK | Verified referential key |
| `date` | `DATE` | Non-Null | ISO Date | Rescued from 3 heterogeneous date formats (`DD/MM/YYYY`, `MM/DD/YYYY`, timestamps) |
| `present_students` | `INTEGER` | Non-Null | 0 to Enrollment | Count of pupils present on session |
| `total_students` | `INTEGER` | Non-Null | > 0 | Total pupil enrollment registered for session |
| `attendance_rate` | `DOUBLE` | Non-Null | 0.0% to 100.0% | Weighted ratio: `present_students * 100.0 / total_students` |
| `quality_status` | `VARCHAR` | Non-Null | `VALID`, `FLAGGED` | Gate 3 result: 214 rows where present < 0 or present > total marked `FLAGGED` (quarantined) |
| `is_proxy_attendance` | `BOOLEAN` | Non-Null | `TRUE`, `FALSE` | Flagged when reconstructed via median imputation |

---

### 2.2 `fact_assessment` (FLN Assessment Fact)
- **Granularity:** 1 row per school per grade per subject assessment
- **Row Count:** 8,000 evaluations
- **Foreign Keys:** `school_id` -> `dim_school.school_id`

| Column Name | Data Type | Null Semantics | Range | Transformation & Quality Logic |
|---|---|---|---|---|
| `assessment_id` | `VARCHAR` | Non-Null | Canonical ID | Primary key |
| `school_id` | `VARCHAR` | Non-Null | Valid `dim_school` FK | Referential link |
| `grade_number` | `INTEGER` | Non-Null | 1 to 10 | Standardized grade cohort |
| `subject_standard` | `VARCHAR` | Non-Null | Mathematics, Language, Science, Social Studies, English, Environmental | Standardized subject taxonomy |
| `normalized_score_pct` | `DOUBLE` | Non-Null | 0.0 to 100.0 | Normalized scale; CBSE letter-grades mapped to midpoints (A=95, B=80, C=65, D=50, E=35) |
| `is_letter_grade_proxy`| `BOOLEAN`| Non-Null | `TRUE`, `FALSE` | Provenance flag indicating deterministic midpoint conversion |

---

### 2.3 `fact_infrastructure` (Physical Infrastructure Fact)
- **Granularity:** 1 row per school per physical amenity evaluated
- **Row Count:** 3,000 records (600 schools × 5 core amenities)

| Column Name | Data Type | Null Semantics | Allowed Values | Transformation & Quality Logic |
|---|---|---|---|---|
| `school_id` | `VARCHAR` | Non-Null | Valid `dim_school` FK | School link |
| `amenity_type` | `VARCHAR` | Non-Null | `electricity`, `drinking_water`, `functional_toilet`, `boundary_wall`, `playground` | 5 statutory infrastructure requirements |
| `amenity_status` | `BOOLEAN` | Tri-State Nullable | `TRUE`, `FALSE`, `NULL` | **Three-valued boolean logic:** `TRUE` (Available), `FALSE` (Missing), `NULL` (UNKNOWN); UNKNOWN is never coerced to FALSE |
| `verification_date` | `DATE` | Nullable | ISO Date | Date of physical site inspection |

---

### 2.4 `fact_procurement` (Mid-Day Meal Procurement Fact)
- **Granularity:** 1 row per delivery invoice batch
- **Row Count:** 12,000 procurement deliveries

| Column Name | Data Type | Null Semantics | Range / Units | Transformation & Quality Logic |
|---|---|---|---|---|
| `invoice_id` | `VARCHAR` | Non-Null | Unique string | Invoice identifier |
| `school_id` | `VARCHAR` | Non-Null | Valid `dim_school` FK | School link |
| `grain_key` | `INTEGER` | Non-Null | 1 to 4 | Commodity FK |
| `quantity_kg` | `DOUBLE` | Non-Null | > 0.0 KG | Standardized from grams, quintals, and bags into standard Kilograms |
| `total_cost` | `DOUBLE` | Non-Null | > ₹0.00 INR | Currency sanitized: stripped '₹', 'INR', spaces, and thousands commas |
| `cost_per_kg` | `DOUBLE` | Non-Null | INR / KG | Unit rate: `total_cost / quantity_kg` |

---

## 3. Governed Analytical Views

| View Name | Materialized In | Base Tables | Authoritative Business Purpose |
|---|---|---|---|
| `school_performance` | `data/processed/edupulse.duckdb` | `fact_attendance`, `fact_assessment` | Institutional attendance rate, assessment count, FLN mean score |
| `district_performance`| `data/processed/edupulse.duckdb` | `school_performance`, `dim_school` | District-level weighted attendance, FLN averages, school counts |
| `school_welfare` | `data/processed/edupulse.duckdb` | `fact_infrastructure` | 5 amenity statuses and physical Infrastructure Readiness Index (0–100%) |
| `school_risk` | `data/processed/edupulse.duckdb` | `school_performance`, `school_welfare` | Multi-factor Risk Severity Score (0–100) and dominant deficit driver |
| `school_intervention_priority`| `data/processed/edupulse.duckdb` | `school_risk`, `district_performance` | Administrative triage sequence (0–100) factoring relative district gaps |
| `school_welfare_gap` | `data/processed/edupulse.duckdb` | `school_performance`, `school_welfare` | 2×2 Welfare Gap Matrix classification (Critical, Resilient, Vulnerable, Model) |
| `procurement_summary`| `data/processed/edupulse.duckdb` | `fact_procurement`, `dim_school` | Aggregate school spend, quantity, cost per student |
| `procurement_anomalies`| `data/processed/edupulse.duckdb` | `procurement_summary` | 18 Peer Benchmark Exceptions exceeding 75th percentile + 1.5 IQR spend/pupil |
| `school_data_quality`| `data/processed/edupulse.duckdb` | All fact tables | Record counts, flagged counts, school completeness percentage |
