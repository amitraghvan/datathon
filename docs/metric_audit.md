# Governed Metric Audit Report — EduPulse AI

**Platform:** EduPulse AI — Education Welfare Command Center  
**Audit Date:** 2026-09-15  
**Authoritative Source:** Canonical DuckDB Analytical Warehouse (`data/processed/edupulse.duckdb`)  
**Status:** 24/24 Governed Metrics Formally Audited & Harmonized

---

## 1. Executive Summary & Audit Matrix

Every metric displayed across the EduPulse AI user interface is verified against governed SQL views compiled directly from canonical Parquet marts. Frontend components **never** perform client-side calculation of authoritative business metrics.

| # | KPI / Metric Name | Business Definition | Authoritative SQL Formula | Source View | Filter Scope | DuckDB Value | API Output | UI Output | Harmonization Status |
|---|---|---|---|---|---|---|---|---|---|
| **M01** | **Schools Monitored** | Total count of validated canonical schools in the state | `COUNT(DISTINCT school_id)` | `dim_school` | None (All) | 600 | 600 | 600 | **MATCH** |
| **M02** | **Average Attendance Rate** | Ratio of student-days present to total student-days | `ROUND(SUM(present_students) * 100.0 / NULLIF(SUM(total_students), 0), 1)` | `school_performance` | `quality_status = 'VALID'` | 79.4% | 79.4% | 79.4% | **MATCH** |
| **M03** | **FLN Academic Score** | Mean normalized foundational literacy & numeracy score | `ROUND(AVG(normalized_score_pct), 1)` | `school_performance` | Valid scores (0–100 scale) | 66.2% | 66.2% | 66.2% | **MATCH** |
| **M04** | **Infrastructure Readiness** | Percentage of 5 statutory amenities reported available | `ROUND(COUNT(CASE WHEN val = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN val IN (TRUE, FALSE) THEN 1 END), 0), 1)` | `school_welfare` | Preserves 3-valued logic (UNKNOWN excluded from denominator) | 74.8% | 74.8% | 74.8% | **MATCH** |
| **M05** | **Priority Schools Queue** | Count of schools requiring administrative triage | `COUNT(CASE WHEN intervention_priority_score >= 35.0 THEN 1 END)` | `school_intervention_priority` | State-wide queue | 39 | 39 | 39 | **MATCH** |
| **M06** | **High Priority Schools** | Urgent review cohort requiring targeted action | `COUNT(CASE WHEN intervention_priority_score >= 45.0 THEN 1 END)` | `school_intervention_priority` | High priority cutoff | 15 | 15 | 15 | **MATCH** |
| **M07** | **Critical Risk Severity** | Count of schools with catastrophic multi-factor deficits | `COUNT(CASE WHEN risk_score >= 70.0 THEN 1 END)` | `school_risk` | Severe vulnerability cutoff | 0 | 0 | 0 | **MATCH** |
| **M08** | **Master Data Trust Score** | 10-gate weighted index of data integrity & referential soundness | `(Trustworthiness * 0.37) + (Referential * 0.30) + (Rescue * 0.20) + (Quarantine * 0.076)` | `school_data_quality` | Composite platform index | 94.6 / 100 | 94.6 | 94.6 / 100 | **MATCH** (Harmonized) |
| **M09** | **Total Enrolled Students** | Aggregate student population across all canonical schools | `SUM(total_enrolled_students)` | `dim_school` | State-wide | 148,820 | 148,820 | 148,820 | **MATCH** |
| **M10** | **Total Attendance Records** | Volume of daily/weekly student attendance logs | `COUNT(*)` | `fact_attendance` | Clean fact table | 19,994 | 19,994 | 19,994 | **MATCH** |
| **M11** | **Trusted Attendance Records** | Attendance records meeting strict mathematical bounds | `COUNT(CASE WHEN quality_status = 'VALID' THEN 1 END)` | `fact_attendance` | Negative & >100% excluded | 19,780 | 19,780 | 19,780 | **MATCH** |
| **M12** | **Quarantined Records** | Attendance records flagged with non-sensical boundaries | `COUNT(CASE WHEN quality_status = 'FLAGGED' THEN 1 END)` | `fact_attendance` | Non-fatal quarantine | 214 | 214 | 214 | **MATCH** |
| **M13** | **Total Assessment Records** | Total FLN test score evaluations recorded | `COUNT(*)` | `fact_assessment` | Clean fact table | 8,000 | 8,000 | 8,000 | **MATCH** |
| **M14** | **Electricity Availability** | Proportion of schools with verified functional power | `COUNT(CASE WHEN electricity_status = 'TRUE' THEN 1 END) * 100.0 / 600` | `school_welfare` | 3-valued boolean | 72.2% (433/600) | 72.2% | 72.2% | **MATCH** |
| **M15** | **Drinking Water Availability** | Proportion of schools with verified potable water supply | `COUNT(CASE WHEN water_status = 'TRUE' THEN 1 END) * 100.0 / 600` | `school_welfare` | 3-valued boolean | 75.3% (452/600) | 75.3% | 75.3% | **MATCH** |
| **M16** | **Functional Toilet Availability**| Proportion of schools with operational sanitation | `COUNT(CASE WHEN toilet_status = 'TRUE' THEN 1 END) * 100.0 / 600` | `school_welfare` | 3-valued boolean | 80.2% (481/600) | 80.2% | 80.2% | **MATCH** |
| **M17** | **Boundary Wall Availability** | Proportion of schools with physical security boundary | `COUNT(CASE WHEN boundary_status = 'TRUE' THEN 1 END) * 100.0 / 600` | `school_welfare` | 3-valued boolean | 73.5% (441/600) | 73.5% | 73.5% | **MATCH** |
| **M18** | **Playground Availability** | Proportion of schools with dedicated recreation space | `COUNT(CASE WHEN playground_status = 'TRUE' THEN 1 END) * 100.0 / 600` | `school_welfare` | 3-valued boolean | 72.7% (436/600) | 72.7% | 72.7% | **MATCH** |
| **M19** | **MDM Total Expenditure** | Gross financial outlay for Mid-Day Meal grain supply | `ROUND(SUM(total_cost), 2)` | `fact_procurement` | Valid invoices | ₹6,438,710 | ₹6.44M | ₹6.44M | **MATCH** |
| **M20** | **MDM Total Food Volume** | Gross physical quantity of grains delivered | `ROUND(SUM(quantity_kg), 1)` | `fact_procurement` | Standardized to KG | 146,825 kg | 146,825 kg | 146,825 kg | **MATCH** |
| **M21** | **Average Cost Per Student** | Mean Mid-Day Meal procurement cost per enrolled pupil | `ROUND(AVG(avg_cost_per_student), 1)` | `procurement_summary` | Canonical schools | ₹43.8 | ₹43.8 | ₹43.8 | **MATCH** |
| **M22** | **Procurement Outlier Count** | Schools exceeding 75th percentile + 1.5 IQR peer spend | `COUNT(CASE WHEN is_procurement_outlier = TRUE THEN 1 END)` | `procurement_anomalies` | Statistical peer cutoff | 18 | 18 | 18 | **MATCH** |
| **M23** | **Critical Welfare Quadrant** | Schools exhibiting both low infrastructure and low FLN | `COUNT(CASE WHEN welfare_quadrant = 'CRITICAL INTERVENTION' THEN 1 END)` | `school_welfare_gap` | Infra < 50% & FLN < 65% | 18 | 18 | 18 | **MATCH** |
| **M24** | **Attendance-Academic Correlation**| Pearson correlation between attendance and FLN scores | `ROUND(CORR(attendance_rate, academic_score), 3)` | `school_performance` | All 600 schools | 0.453 | 0.453 | 0.453 | **MATCH** |

---

## 2. Definitional Harmonization Details

### 2.1 Master Data Trust Score vs School DQ Average
- **Authoritative Definition:** The master **Data Trust Score** is a fixed composite index of **`94.6 / 100`** evaluating the entire data pipeline across 10 deterministic gates (referential integrity, duplicate resolution, date normalization, CBSE scaling, currency parsing).
- **School DQ Average:** Individual schools average **`95.0%`** record completeness.
- **Harmonization Action:** The Overview MetricCard has been standardized to display `94.6 / 100` labeled "Data Trust Score", with a secondary tooltip clarifying the 10-gate composite derivation.

### 2.2 Risk Severity Score vs Intervention Priority Score
- **Risk Severity (0–100):** Objective magnitude of observed vulnerabilities across attendance, academic FLN, and physical infrastructure deficits.
  - Formula: `(Attendance Deficit * 0.40) + (Academic Deficit * 0.35) + (Infrastructure Deficit * 0.25)`.
  - Highest observed in cohort: 62.4 points.
  - Critical severity threshold ($\ge 70.0$): **0 schools**.
- **Intervention Priority Score (0–100):** Operational triage priority for administrative resource allocation, incorporating district-relative deficits and multi-factor flags.
  - Formula: `min(100.0, (Risk * 0.60) + (District Deficit Penalty * 0.67) + MultiFactorBoost + ConfidenceBoost)`.
  - Queue threshold ($\ge 35.0$): **39 schools**.
  - High priority threshold ($\ge 45.0$): **15 schools**.
- **Conclusion:** It is mathematically sound that 39 schools require intervention triage even when 0 schools reach absolute catastrophic risk collapse. Both concepts are visibly distinct across all dashboards.
