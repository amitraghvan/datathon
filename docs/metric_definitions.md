# EDUPULSE AI — Canonical Metric Definitions & Governance Contract
## Track 4: Education & EdTech — Student Retention & Welfare Efficacy Tracker

---

## 1. Principles of Metric Governance

To maintain enterprise data trust and consulting-grade defensibility:
1. **Mathematical Precision**: Every metric is defined with an unambiguous mathematical formula.
2. **Operational Weighting**: Aggregations reflect real student population volume; simple unweighted averages of percentages across disparate group sizes are prohibited where volume distortion would occur.
3. **Data Quality Exclusions**: Anomalous or corrupted records (impossible student counts, Sunday proxy logs) are explicitly quarantined from trusted KPI calculations.
4. **Coverage Transparency**: Every reported KPI must carry a data coverage indicator expressing the proportion of valid observations backing the metric.
5. **No False Equivalence**: Analytical proxies (e.g. letter-grade midpoints) are documented as comparative proxies, never as official statutory equivalences.

---

## 2. Core Operational Metric Contracts

### A. Student Attendance Rate (`attendance_rate`)
- **Business Meaning**: The proportion of enrolled students physically present in school on scheduled instructional days.
- **Formula**:
  $$\text{Attendance Rate} = \frac{\sum_{i \in \text{Trusted}} \text{present\_students}_i}{\sum_{i \in \text{Trusted}} \text{total\_students}_i} \times 100$$
- **Grain**: Daily per grade per school $\to$ Aggregated to school and district levels.
- **Source Tables**: `fact_attendance`, `dim_school`, `dim_date`.
- **Filters & Exclusions**:
  - `is_trusted_attendance = TRUE`
  - Excludes `is_impossible_attendance = TRUE` (`present_students > total_students`).
  - Excludes `is_proxy_attendance = TRUE` (100% attendance recorded on Sundays).
  - Excludes `total_students <= 0`.
- **Aggregation Policy**: **Weighted Aggregation**. Student counts are summed across days before division to avoid distortion caused by variable attendance reporting.
- **Coverage Indicator**:
  $$\text{Coverage Rate} = \frac{\text{Count of Trusted Daily Records}}{\text{Total Operational Attendance Records}} \times 100$$
- **Known Limitations**: Does not distinguish excused medical absences from unexcused truancy.

---

### B. Normalized FLN Academic Score (`academic_score`)
- **Business Meaning**: Standardized student learning outcome index across Foundational Literacy & Numeracy (FLN) assessments on a common $0.0 - 100.0\%$ scale.
- **Formula**:
  $$\text{Academic Score} = \frac{\sum_{j \in \text{Valid}} (\text{normalized\_score\_pct}_j \times \text{students\_assessed}_j)}{\sum_{j \in \text{Valid}} \text{students\_assessed}_j}$$
- **Grain**: Per assessment administration $\to$ Aggregated to school, grade, subject, and district.
- **Source Tables**: `fact_assessment`, `dim_school`, `dim_subject`.
- **Standardization Methods**:
  - `Percentage / pct / %`: $\text{Raw Score}$.
  - `CGPA (10-point)`: $\text{CGPA} \times 10.0$.
  - `Raw Marks`: $\frac{\text{Numerator}}{\text{Denominator}} \times 100.0$.
  - `Letter Grade (Mid-point Proxy)`: $A+=95, A=85, B=75, C=65, D=50, E=35$.
- **Filters & Exclusions**:
  - `quality_status = 'VALID'`
  - Excludes unparseable scores or scores outside $[0.0, 100.0]$.
- **Sensitivity Policy**: Flag `is_letter_grade_proxy` allows analytical runs with and without proxy grades to verify statistical stability.
- **Known Limitations**: Letter grade midpoint mapping has lower variance than continuous percentages.

---

### C. Infrastructure Readiness Index (`infrastructure_readiness`)
- **Business Meaning**: A multi-factor composite index evaluating school amenity availability and basic welfare functionality.
- **Formula**:
  $$\text{Readiness Index} = \left( \sum_{k=1}^5 w_k \times S_k \right) \times 100$$
  Where:
  - Functional Toilets ($w = 0.30$): $\text{Score} = 1.0 \text{ (TRUE)}, 0.0 \text{ (FALSE)}, 0.5 \text{ (UNKNOWN)}$.
  - Drinking Water ($w = 0.30$): $\text{Score} = 1.0 \text{ (TRUE)}, 0.0 \text{ (FALSE)}, 0.5 \text{ (UNKNOWN)}$.
  - Electricity ($w = 0.20$): $\text{Score} = 1.0 \text{ (TRUE)}, 0.0 \text{ (FALSE)}, 0.5 \text{ (UNKNOWN)}$.
  - Boundary Wall ($w = 0.10$): $\text{Score} = 1.0 \text{ (TRUE)}, 0.0 \text{ (FALSE)}, 0.5 \text{ (UNKNOWN)}$.
  - Playground ($w = 0.10$): $\text{Score} = 1.0 \text{ (TRUE)}, 0.0 \text{ (FALSE)}, 0.5 \text{ (UNKNOWN)}$.
- **Grain**: Latest recorded inspection per school $\to$ Aggregated to district.
- **Source Tables**: `fact_infrastructure`, `dim_school`.
- **Filters & Exclusions**: Uses the most recent inspection record (`ROW_NUMBER() OVER(PARTITION BY school_id ORDER BY date DESC) = 1`).
- **Policy on Missingness**: Missing amenities (`UNKNOWN`) are assigned $0.5$ neutral weight to distinguish uninspected amenities from confirmed broken facilities ($0.0$).
- **Known Limitations**: Relies on periodic periodic physical inspection frequency.

---

### D. Total Procurement Spend (`procurement_spend`)
- **Business Meaning**: Cumulative financial expenditure on Mid-Day Meal (MDM) food commodities in Indian Rupees (INR).
- **Formula**:
  $$\text{Total Spend} = \sum \text{total\_cost\_inr}$$
- **Grain**: Per procurement order $\to$ Aggregated to school, vendor, grain, and district.
- **Source Tables**: `fact_procurement`, `dim_vendor`, `dim_grain`.
- **Value Rescue Policy**: Where cost was missing in source files, it is derived via $\text{Quantity (kg)} \times \text{Official Price Schedule}$.
- **Known Limitations**: Excludes transportation/logistics costs not recorded in raw invoices.

---

### E. Procurement Cost Per Student (`procurement_cost_per_student`)
- **Business Meaning**: Annualized nutritional welfare expenditure allocated per enrolled student.
- **Formula**:
  $$\text{Cost Per Student} = \frac{\text{Total Spend (INR)}}{\text{Total Enrolled Students}}$$
- **Source Tables**: `procurement_summary` (View), `dim_school`.
- **Zero Handling**: Safe division using `NULLIF(total_enrolled_students, 0)`.

---

### F. Average Procurement Cost Per KG (`procurement_cost_per_kg`)
- **Business Meaning**: Weighted average commodity cost per kilogram across all grains delivered.
- **Formula**:
  $$\text{Cost Per KG} = \frac{\sum \text{total\_cost\_inr}}{\sum \text{quantity\_kg}}$$
- **Benchmark Bounds**: Constrained by statutory schedule ($₹30 - ₹120/\text{kg}$). Any order yielding $< ₹25$ or $> ₹130/\text{kg}$ is flagged for price variance review.

---

### G. Operational Data Quality Rate (`data_quality_rate`)
- **Business Meaning**: Proportion of operational transaction records adhering to all validation and referential trust criteria without requiring exclusion.
- **Formula**:
  $$\text{Quality Rate} = \frac{\text{Trusted Records (Attendance + Assessment + Procurement)}}{\text{Total Records Processed}} \times 100$$
- **Source Tables**: `school_data_quality` (View).

---

## 3. Phase 4 Risk Intelligence & Advanced Metric Contracts

### H. Retention Risk Proxy (`risk_score`)
- **Business Meaning**: Multi-factor institutional vulnerability score (0.0–100.0) reflecting compound deficits in student attendance, academic performance, and school infrastructure.
- **Formula**:
  $$\text{Risk Score} = 0.45 \times R_{\text{att}} + 0.35 \times R_{\text{acad}} + 0.20 \times R_{\text{infra}}$$
  Where $R_i = \max(0.0, \min(100.0, 100.0 - \text{Metric}_i))$.
- **Source Views / Tables**: `school_risk` (View), `school_risk.parquet`.
- **Dynamic Re-normalization**: If one component is missing, weights re-normalize over the remaining sum. If $>1$ is missing, score is `NULL` (`INSUFFICIENT_DATA`).
- **Tiers**: LOW ($0 - 24.9$), MODERATE ($25 - 49.9$), HIGH ($50 - 74.9$), CRITICAL ($75 - 100.0$).
- **Strict Guardrail**: NOT a verified student dropout prediction; serves as an operational triaging proxy.

---

### I. Intervention Priority Score (`intervention_priority_score`)
- **Business Meaning**: Operational ranking metric answering which schools require immediate administrative attention and supervisory visits.
- **Formula**:
  $$P = \min\left(100.0, (R \times 0.60) + (\min(30.0, D_{\text{penalty}}) \times 0.67) + B_{\text{multi}} + B_{\text{conf}}\right)$$
  Where $D_{\text{penalty}}$ evaluates negative gaps relative to district peers, $B_{\text{multi}} = 10.0$ for multi-factor vulnerability, and $B_{\text{conf}} = 10.0$ for high coverage.
- **Source Views / Tables**: `school_intervention_priority` (View), `school_intervention_priority.parquet`.
- **Ranking**: Deterministic rank `intervention_rank` ordered by Priority Score (DESC), Enrollment (DESC), School ID (ASC).

---

### J. District Benchmark Gaps (`attendance_gap_vs_district`, `academic_gap_vs_district`, `infrastructure_gap_vs_district`)
- **Business Meaning**: School performance relative to its administrative district peer mean.
- **Formula**:
  $$\Delta_{\text{metric}} = \text{School Metric} - \text{District Mean Metric}$$
- **Source Views / Tables**: `school_intervention_priority` (View), `school_risk.parquet`.

---

### K. Welfare Gap Matrix Quadrants (`welfare_quadrant`)
- **Business Meaning**: 2x2 categorical matrix classifying schools on physical infrastructure readiness ($\ge 50\%$) vs academic learning score ($\ge 65\%$).
- **Quadrants**:
  1. `MODEL`: High Infra $\ge 50\%$, High Acad $\ge 65\%$
  2. `RESILIENT`: Low Infra $< 50\%$, High Acad $\ge 65\%$
  3. `ACADEMIC INTERVENTION`: High Infra $\ge 50\%$, Low Acad $< 65\%$
  4. `CRITICAL INTERVENTION`: Low Infra $< 50\%$, Low Acad $< 65\%$
- **Source Views / Tables**: `school_welfare_gap` (View), `school_welfare_gap.parquet`.

---

### L. School Cluster Profiles (`cluster_id`, `cluster_name`)
- **Business Meaning**: Empirical school archetypes derived from standardized K-Means clustering ($K=4$, $\text{Silhouette}=0.216$) across attendance, academics, infrastructure, and procurement spend.
- **Profiles**:
  - `0`: Strong Performance & Well Supported
  - `1`: Academic Support Needed
  - `2`: Welfare & Infrastructure Constrained
  - `3`: Multi-Factor Critical Priority
- **Source Tables**: `school_segmentation` (Table), `school_segmentation.parquet`.

