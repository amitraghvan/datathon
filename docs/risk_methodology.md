# EDUPULSE AI — Retention & Intervention Intelligence Methodology
## Governed Methodology, Mathematical Foundations & Analytical Safeguards
**Track 4: Education & EdTech — Student Retention & Welfare Efficacy Tracker**

---

## 1. Business Objective

The primary objective of the **EduPulse AI Risk Intelligence Engine** is to provide educational administrators and district education officers (DEOs) with a defensible, explainable, and reproducible decision-support system to answer:
1. **Which schools require operational and pedagogical attention first?**
2. **What underlying factors (attendance, academic deficits, physical amenities) drive this priority?**
3. **What specific, actionable intervention is appropriate for each school?**
4. **Where are vulnerable schools geographically concentrated?**

By moving from reactive administration to proactive welfare intelligence, the state can prioritize resource allocation, emergency maintenance grants, and remedial education where evidence shows the greatest compound need.

---

## 2. What the Risk Score Means vs. What It Does NOT Mean

### Explicit Governance Safeguards

> [!IMPORTANT]
> **What the Retention Risk Proxy IS:**
> - A **multi-factor vulnerability proxy** combining student attendance deficits, academic learning shortfalls, and physical infrastructure constraints.
> - An **operational triaging instrument** designed to rank schools for administrative review and targeted support.
> - A **coverage-aware indicator** that reflects the depth and trustworthiness of available evidence.

> [!CAUTION]
> **What the Retention Risk Proxy IS NOT:**
> - **NOT a verified student dropout prediction.** The competition datasets provide cross-sectional operational records but do NOT contain ground-truth longitudinal student dropout labels. Claiming to predict individual or school-level student dropouts without historical target labels would be scientifically fraudulent.
> - **NOT a causal diagnosis.** While attendance and academic performance exhibit statistical association ($r = 0.45, p < 0.001$), this system does NOT claim that lower attendance directly causes lower test scores, nor that repairing a toilet will unilaterally raise test scores.
> - **NOT a punitive evaluation.** The score measures institutional need for support, not administrative failure or teacher blameworthiness.

---

## 3. Mathematical Formulation & Component Weights

The composite Retention Risk Proxy ($R \in [0.0, 100.0]$) is computed as a weighted linear combination of three standardized domain vulnerabilities:

$$R = w_{\text{att}} \cdot R_{\text{attendance}} + w_{\text{acad}} \cdot R_{\text{academic}} + w_{\text{infra}} \cdot R_{\text{infrastructure}}$$

Where baseline policy weights are configured as:
- **Attendance Risk ($w_{\text{att}} = 0.45$, 45%)**: Leading proxy for student engagement and disengagement risk.
- **Academic Risk ($w_{\text{acad}} = 0.35$, 35%)**: Direct measure of foundational learning deficit (FLN scores).
- **Infrastructure Risk ($w_{\text{infra}} = 0.20$, 20%)**: Structural enabling environment (sanitation, drinking water, power, security).

Each component vulnerability is scaled from $0.0$ (no concern / perfect performance) to $100.0$ (maximum deficit / total absence):

$$\sum w_i = 0.45 + 0.35 + 0.20 = 1.00$$

---

## 4. Component Risk Formulations

### A. Attendance Risk ($R_{\text{attendance}}$)
$$\text{Attendance Risk} = \max\left(0.0, \min\left(100.0, 100.0 - \text{Weighted Attendance Rate}\right)\right)$$
- **Trusted Record Filter**: Computed strictly on verified instructional days (`is_trusted_attendance = TRUE`).
- **Quarantine Policy**: Excludes 835 impossible attendance records (`present > total`) and 1,011 Sunday proxy records (`100% attendance on Sunday`).
- **Coverage & Status Tracking**:
  - `SUFFICIENT`: $\ge 25$ daily records ($\text{Coverage} \ge 83\%$).
  - `LIMITED`: $10 - 24$ daily records ($33\% \le \text{Coverage} < 83\%$).
  - `INSUFFICIENT`: $< 10$ daily records ($\text{Coverage} < 33\%$).

### B. Academic Risk ($R_{\text{academic}}$)
$$\text{Academic Risk} = \max\left(0.0, \min\left(100.0, 100.0 - \text{Normalized FLN Academic Score}\right)\right)$$
- **Trusted Record Filter**: Computed strictly on valid assessment administrations (`quality_status = 'VALID'`).
- **Dual Metric Preservation**: To protect against proxy bias, the system tracks both `academic_score` (all valid records including letter-grade midpoint proxies) and `numeric_only_academic_score` (continuous percentage/marks records only).
- **Coverage & Status Tracking**:
  - `SUFFICIENT`: $\ge 10$ test records ($\text{Coverage} \ge 83\%$).
  - `LIMITED`: $4 - 9$ test records ($33\% \le \text{Coverage} < 83\%$).
  - `INSUFFICIENT`: $< 4$ test records ($\text{Coverage} < 33\%$).

### C. Infrastructure Risk ($R_{\text{infrastructure}}$)
$$\text{Infrastructure Risk} = \max\left(0.0, \min\left(100.0, 100.0 - \text{Infrastructure Readiness Index}\right)\right)$$
- **Welfare Index Composition**: Functional Toilets ($30\%$), Drinking Water ($30\%$), Electricity ($20\%$), Boundary Wall ($10\%$), Playground ($10\%$).
- **The Principle of Truth in Absence**: Missing amenity data is categorized as `UNKNOWN` and assigned a neutral $0.5$ weight. It is **NEVER** treated as `FALSE` ($0.0$).
- **Amenity Audit Counts**: For every school, the engine tracks `known_amenity_count` (confirmed TRUE or FALSE) and `unknown_amenity_count`.
- **Coverage & Status Tracking**:
  - `SUFFICIENT`: Known amenities $\ge 4/5$ ($\text{Coverage} \ge 80\%$).
  - `LIMITED`: Known amenities $2 - 3/5$ ($40\% \le \text{Coverage} < 80\%$).
  - `INSUFFICIENT`: Known amenities $\le 1/5$ ($\text{Coverage} < 40\%$).

---

## 5. Dynamic Coverage-Aware Re-Normalization & Missing Data Handling

A fatal flaw in standard risk engines is that missing data either defaults to zero (hiding risk) or 100 (manufacturing artificial panic). 

EduPulse AI implements **Dynamic Coverage-Aware Re-Normalization**:

1. **At Least Two Major Components Present**:
   If one domain is completely unrecorded (e.g. no physical inspection conducted yet), the remaining valid components are dynamically re-normalized over their shared weight sum:
   $$\hat{w}_j = \frac{w_j}{\sum_{k \in \text{Available}} w_k}$$
   *Example*: If Infrastructure is unrecorded, Attendance ($45\%$) and Academics ($35\%$) re-normalize to:
   $$\hat{w}_{\text{att}} = \frac{0.45}{0.80} = 56.25\%, \quad \hat{w}_{\text{acad}} = \frac{0.35}{0.80} = 43.75\%$$
2. **More Than One Major Component Missing**:
   $$\text{Risk Score} = \text{NULL}, \quad \text{Risk Status} = \text{'INSUFFICIENT\_DATA'}$$
   The engine refuses to fabricate a score without sufficient empirical support.
3. **Composite Risk Data Coverage**:
   $$\text{Composite Coverage} = (0.45 \times \text{Att Cov}) + (0.35 \times \text{Acad Cov}) + (0.20 \times \text{Infra Cov})$$

---

## 6. Risk Bands & Tiers

The continuous 0–100 risk score is partitioned into four configurable governance tiers:

| Tier | Score Range | Operational Meaning | Recommended Administrative Posture |
| :--- | :--- | :--- | :--- |
| **LOW** | $0.0 - 24.9$ | Well-functioning indicators; minimal institutional vulnerability. | Routine quarterly administrative monitoring; potential peer-mentorship school model. |
| **MODERATE** | $25.0 - 49.9$ | Emerging concerns in single domain; stable overall operations. | Preventative monitoring, automated SMS parent alerts, routine facility repair audit. |
| **HIGH** | $50.0 - 74.9$ | Significant deficits across one or more critical welfare domains. | Targeted pedagogical remediation in FLN, attendance taskforce, infrastructure work order. |
| **CRITICAL** | $75.0 - 100.0$ | Severe, compound failure across multiple welfare and learning dimensions. | Immediate multi-factor emergency intervention taskforce; administrative fast-track grant. |

---

## 7. Deterministic Risk Driver Taxonomy

To prevent subjective or opaque decisions, the risk engine decomposes every school's priority score into deterministic, rank-ordered contributors:

$$\text{Driver Contribution}_i = R_i \times w_i$$

### Controlled Taxonomy
1. `ATTENDANCE`: Student absenteeism / truancy is the largest contributor to risk.
2. `ACADEMIC`: Lagging foundational literacy and numeracy scores represent the primary shortfall.
3. `INFRASTRUCTURE`: Severe amenity deprivation (lack of functional toilets, water, or electricity) drives risk.
4. `MULTI_FACTOR`: **High compound vulnerability** where Attendance Risk $\ge 50.0$ **AND** Academic Risk $\ge 50.0$ **AND** Infrastructure Risk $\ge 50.0$.
5. `DATA_INSUFFICIENT`: Insufficient trusted records to calculate a defensible driver profile.

---

## 8. District Benchmark Gap Analysis

School risk should never be viewed in clinical isolation from regional economic and social conditions. For each school, the engine computes performance gaps relative to its administrative district peers:

$$\Delta_{\text{attendance}} = \text{School Attendance Rate} - \text{District Mean Attendance Rate}$$
$$\Delta_{\text{academic}} = \text{School Academic Score} - \text{District Mean Academic Score}$$
$$\Delta_{\text{infrastructure}} = \text{School Infrastructure Readiness} - \text{District Mean Readiness}$$

A school lagging $-15.0$ percentage points behind its own district average exhibits a localized institutional bottleneck requiring immediate supervision.

---

## 9. Intervention Priority Score Formulation

The **Intervention Priority Score** ($P \in [0.0, 100.0]$) answers the operational question: *"Which school must the inspection team visit first on Monday morning?"*

It synthesizes four distinct governance considerations:

$$P = \min\left(100.0, (R \times 0.60) + (\min(30.0, D_{\text{penalty}}) \times 0.67) + B_{\text{multi}} + B_{\text{conf}}\right)$$

Where:
1. **Absolute Vulnerability Severity ($60\%$)**: Base composite risk score ($R \times 0.60$).
2. **Peer Deficit Penalty ($20\%$)**: Penalizes falling below district peers across attendance, academics, and infrastructure:
   $$D_{\text{penalty}} = 0.4 \times |\Delta_{\text{att}}^-| + 0.4 \times |\Delta_{\text{acad}}^-| + 0.2 \times |\Delta_{\text{infra}}^-|$$
3. **Multi-Factor Compound Boost ($10\%$)**: $+10.0$ points if the primary driver is `MULTI_FACTOR`.
4. **Data Coverage Confidence Boost ($10\%$)**: $+10.0$ points if Composite Coverage $\ge 80\%$, $+5.0$ points otherwise (prevents low-coverage schools from dominating the intervention queue while ensuring verified high-risk schools are prioritized).

### Deterministic Tie-Breaking
Schools are ranked deterministically by:
1. `intervention_priority_score` (Descending)
2. `enrollment` (Descending — larger student populations impacted first)
3. `school_id` (Ascending — canonical alphabetical tie-breaker)

---

## 10. Sensitivity & Robustness Analyses

To verify that analytical conclusions are robust and not artifacts of arbitrary parameter selection, two rigorous sensitivity analyses were conducted across the complete 600-school cohort.

### A. Policy Weight Shift Sensitivity
Rankings were evaluated across four distinct policy weighting regimes:
- **Baseline**: $45\%$ Attendance / $35\%$ Academics / $20\%$ Infrastructure
- **Infrastructure-Heavy**: $40\%$ Attendance / $35\%$ Academics / $25\%$ Infrastructure
- **Attendance-Heavy**: $50\%$ Attendance / $30\%$ Academics / $20\%$ Infrastructure
- **Academic-Heavy**: $35\%$ Attendance / $45\%$ Academics / $20\%$ Infrastructure

#### Empirical Stability Findings:
- **Spearman Rank Correlation**: $\rho \ge 0.985$ across all alternative scenarios against baseline ($p < 0.0001$).
- **Top-10 School Overlap**: $90\% - 100\%$ overlap across scenarios.
- **Conclusion**: Intervention priorities demonstrate **exceptional structural robustness** under reasonable policy weight adjustments.

### B. Letter-Grade Midpoint Proxy Sensitivity
Because letter grades ($A+, A, B, C, D, E$) were normalized using documented midpoint proxies, school FLN rankings were compared between:
1. **All Valid Records** (Continuous + Letter-Grade Proxies)
2. **Numeric-Only Records** (Strictly Continuous Percentages and Marks)

#### Empirical Stability Findings:
- **School-Level Pearson Correlation**: $r = 0.858$ ($p < 0.001$).
- **School-Level Spearman Rank Correlation**: $\rho = 0.857$ ($p < 0.001$).
- **Mean Absolute Academic Score Difference**: Only $2.16$ percentage points.
- **District-Level Pearson Correlation**: $r = 0.984$ ($\rho = 0.967$).
- **Mean Composite Risk Score Impact**: Only $0.76$ points out of $100$.
- **Conclusion**: The letter-grade midpoint conversion introduces negligible distortion into final school intervention prioritization and district ranking.

---

## 11. Known Methodology Limitations

1. **Cross-Sectional Timeframe**: Current datasets reflect a one-year operational window (2025–2026 academic year); multi-year longitudinal drift cannot yet be observed.
2. **Absence of Ground-Truth Dropout Labels**: True dropout status is unrecorded; priority scores strictly reflect multi-factor vulnerability proxies.
3. **Self-Reported Inspection Variance**: School infrastructure assessments depend on periodic inspector visits and subjective remark fields.
4. **Attendance Reason Unavailability**: Administrative logs do not distinguish between excused medical leaves, harvesting season absences, and unexcused chronic absenteeism.
