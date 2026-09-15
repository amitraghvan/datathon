-- ============================================================
-- EDUPULSE AI — GOVERNED ANALYTICAL SQL VIEWS
-- Engine: DuckDB
-- ============================================================

-- ------------------------------------------------------------
-- VIEW 1: school_performance
-- Granularity: One row per school
-- Aggregation Policy:
--   - Attendance is WEIGHTED by student counts across days: SUM(present) / SUM(total)
--   - Academic score is WEIGHTED by student assessment volume
--   - Excludes quarantined impossible/proxy attendance records from trusted KPIs
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW school_performance AS
WITH att_agg AS (
    SELECT
        school_id,
        COUNT(*) AS total_attendance_records,
        SUM(CASE WHEN is_trusted_attendance THEN 1 ELSE 0 END) AS trusted_attendance_records,
        SUM(CASE WHEN is_trusted_attendance THEN present_students ELSE 0 END) AS trusted_present_sum,
        SUM(CASE WHEN is_trusted_attendance THEN total_students ELSE 0 END) AS trusted_total_sum,
        ROUND(
            SUM(CASE WHEN is_trusted_attendance THEN present_students ELSE 0 END) * 100.0 /
            NULLIF(SUM(CASE WHEN is_trusted_attendance THEN total_students ELSE 0 END), 0),
            2
        ) AS weighted_attendance_rate,
        ROUND(
            AVG(CASE WHEN is_trusted_attendance THEN attendance_rate ELSE NULL END),
            2
        ) AS unweighted_attendance_rate
    FROM fact_attendance
    GROUP BY school_id
),
ass_agg AS (
    SELECT
        school_id,
        COUNT(*) AS total_assessment_records,
        SUM(CASE WHEN quality_status = 'VALID' THEN 1 ELSE 0 END) AS valid_assessment_records,
        ROUND(
            SUM(CASE WHEN quality_status = 'VALID' THEN normalized_score_pct * total_students_assessed ELSE 0 END) /
            NULLIF(SUM(CASE WHEN quality_status = 'VALID' THEN total_students_assessed ELSE 0 END), 0),
            2
        ) AS weighted_academic_score,
        ROUND(
            AVG(CASE WHEN quality_status = 'VALID' THEN normalized_score_pct ELSE NULL END),
            2
        ) AS unweighted_academic_score,
        SUM(total_students_assessed) AS total_students_assessed_sum
    FROM fact_assessment
    GROUP BY school_id
)
SELECT
    s.school_id,
    s.school_name,
    s.district,
    s.block,
    s.total_enrolled_students AS enrollment,
    s.school_type,
    s.medium,
    COALESCE(a.weighted_attendance_rate, a.unweighted_attendance_rate, 0.0) AS attendance_rate,
    COALESCE(sc.weighted_academic_score, sc.unweighted_academic_score, 0.0) AS academic_score,
    COALESCE(a.total_attendance_records, 0) AS attendance_records,
    COALESCE(sc.total_assessment_records, 0) AS assessment_records,
    COALESCE(sc.total_students_assessed_sum, 0) AS total_assessed_students,
    ROUND(
        (COALESCE(a.trusted_attendance_records, 0) + COALESCE(sc.valid_assessment_records, 0)) * 100.0 /
        NULLIF(COALESCE(a.total_attendance_records, 0) + COALESCE(sc.total_assessment_records, 0), 0),
        1
    ) AS quality_coverage_pct
FROM dim_school s
LEFT JOIN att_agg a ON s.school_id = a.school_id
LEFT JOIN ass_agg sc ON s.school_id = sc.school_id;

-- ------------------------------------------------------------
-- VIEW 2: school_welfare
-- Granularity: One row per school
-- Evaluates latest infrastructure status and calculates
-- Infrastructure Readiness Index (0.0 to 100.0%)
-- Weights: Toilets 30%, Water 30%, Electricity 20%, Wall 10%, Playground 10%
-- Distinguishes TRUE (1.0), FALSE (0.0), UNKNOWN (0.5 neutral proxy)
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW school_welfare AS
WITH latest_infra AS (
    SELECT
        *,
        ROW_NUMBER() OVER(PARTITION BY school_id ORDER BY date DESC, inspection_id DESC) AS rn
    FROM fact_infrastructure
)
SELECT
    s.school_id,
    s.school_name,
    s.district,
    s.block,
    COALESCE(i.has_electricity, 'UNKNOWN') AS electricity_status,
    COALESCE(i.has_drinking_water, 'UNKNOWN') AS water_status,
    COALESCE(i.has_functional_toilet, 'UNKNOWN') AS toilet_status,
    COALESCE(i.has_boundary_wall, 'UNKNOWN') AS boundary_status,
    COALESCE(i.has_playground, 'UNKNOWN') AS playground_status,
    ROUND(
        (
            (CASE WHEN i.has_functional_toilet = 'TRUE' THEN 1.0 WHEN i.has_functional_toilet = 'FALSE' THEN 0.0 ELSE 0.5 END * 0.30) +
            (CASE WHEN i.has_drinking_water = 'TRUE' THEN 1.0 WHEN i.has_drinking_water = 'FALSE' THEN 0.0 ELSE 0.5 END * 0.30) +
            (CASE WHEN i.has_electricity = 'TRUE' THEN 1.0 WHEN i.has_electricity = 'FALSE' THEN 0.0 ELSE 0.5 END * 0.20) +
            (CASE WHEN i.has_boundary_wall = 'TRUE' THEN 1.0 WHEN i.has_boundary_wall = 'FALSE' THEN 0.0 ELSE 0.5 END * 0.10) +
            (CASE WHEN i.has_playground = 'TRUE' THEN 1.0 WHEN i.has_playground = 'FALSE' THEN 0.0 ELSE 0.5 END * 0.10)
        ) * 100.0,
        1
    ) AS infrastructure_readiness_pct,
    COALESCE(i.remarks, 'No inspection on record') AS latest_remarks
FROM dim_school s
LEFT JOIN latest_infra i ON s.school_id = i.school_id AND i.rn = 1;

-- ------------------------------------------------------------
-- VIEW 3: district_performance
-- Granularity: One row per district
-- Roll-up of school performance, welfare, and data trust metrics
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW district_performance AS
SELECT
    p.district,
    COUNT(DISTINCT p.school_id) AS school_count,
    SUM(p.enrollment) AS total_enrolled_students,
    ROUND(AVG(p.attendance_rate), 2) AS avg_attendance_rate,
    ROUND(AVG(p.academic_score), 2) AS avg_academic_score,
    ROUND(AVG(w.infrastructure_readiness_pct), 1) AS avg_infrastructure_readiness,
    SUM(CASE WHEN p.quality_coverage_pct >= 90.0 THEN 1 ELSE 0 END) AS high_quality_school_count,
    ROUND(AVG(p.quality_coverage_pct), 1) AS data_quality_coverage_pct
FROM school_performance p
LEFT JOIN school_welfare w ON p.school_id = w.school_id
GROUP BY p.district;

-- ------------------------------------------------------------
-- VIEW 4: procurement_summary
-- Granularity: One row per school
-- Aggregates MDM grain supply volume, expenditure, and unit metrics
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW procurement_summary AS
WITH proc_agg AS (
    SELECT
        school_id,
        COUNT(*) AS total_procurement_transactions,
        ROUND(SUM(quantity_kg), 2) AS total_quantity_kg,
        ROUND(SUM(total_cost), 2) AS total_spend_inr,
        COUNT(DISTINCT grain_standard) AS distinct_grains_count,
        COUNT(DISTINCT vendor_id) AS distinct_vendors_count,
        ROUND(SUM(CASE WHEN grain_standard = 'Rice' THEN quantity_kg ELSE 0 END), 2) AS rice_kg,
        ROUND(SUM(CASE WHEN grain_standard = 'Wheat' THEN quantity_kg ELSE 0 END), 2) AS wheat_kg,
        ROUND(SUM(CASE WHEN grain_standard = 'Pulses' THEN quantity_kg ELSE 0 END), 2) AS pulses_kg,
        ROUND(SUM(CASE WHEN grain_standard = 'Cooking Oil' THEN quantity_kg ELSE 0 END), 2) AS oil_kg
    FROM fact_procurement
    GROUP BY school_id
)
SELECT
    s.school_id,
    s.school_name,
    s.district,
    s.block,
    s.total_enrolled_students AS enrollment,
    COALESCE(p.total_procurement_transactions, 0) AS procurement_records,
    COALESCE(p.total_quantity_kg, 0.0) AS total_quantity_kg,
    COALESCE(p.total_spend_inr, 0.0) AS total_spend_inr,
    ROUND(
        COALESCE(p.total_spend_inr, 0.0) / NULLIF(p.total_quantity_kg, 0),
        2
    ) AS avg_cost_per_kg,
    ROUND(
        COALESCE(p.total_spend_inr, 0.0) / NULLIF(s.total_enrolled_students, 0),
        2
    ) AS avg_cost_per_student,
    ROUND(
        COALESCE(p.total_quantity_kg, 0.0) / NULLIF(s.total_enrolled_students, 0),
        2
    ) AS avg_kg_per_student,
    COALESCE(p.distinct_grains_count, 0) AS grain_count,
    COALESCE(p.distinct_vendors_count, 0) AS vendor_count,
    COALESCE(p.rice_kg, 0.0) AS rice_kg,
    COALESCE(p.wheat_kg, 0.0) AS wheat_kg,
    COALESCE(p.pulses_kg, 0.0) AS pulses_kg,
    COALESCE(p.oil_kg, 0.0) AS oil_kg
FROM dim_school s
LEFT JOIN proc_agg p ON s.school_id = p.school_id;

-- ------------------------------------------------------------
-- VIEW 5: school_data_quality
-- Granularity: One row per school
-- Multi-domain quality matrix (Attendance + Assessment + Infra + MDM)
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW school_data_quality AS
WITH att_q AS (
    SELECT
        school_id,
        COUNT(*) AS att_total,
        SUM(CASE WHEN is_trusted_attendance THEN 1 ELSE 0 END) AS att_trusted,
        SUM(CASE WHEN is_impossible_attendance THEN 1 ELSE 0 END) AS att_impossible,
        SUM(CASE WHEN is_proxy_attendance THEN 1 ELSE 0 END) AS att_proxy
    FROM fact_attendance
    GROUP BY school_id
),
ass_q AS (
    SELECT
        school_id,
        COUNT(*) AS ass_total,
        SUM(CASE WHEN quality_status = 'VALID' THEN 1 ELSE 0 END) AS ass_valid,
        SUM(CASE WHEN is_letter_grade_proxy THEN 1 ELSE 0 END) AS ass_proxy_letter
    FROM fact_assessment
    GROUP BY school_id
),
pro_q AS (
    SELECT
        school_id,
        COUNT(*) AS pro_total,
        SUM(CASE WHEN quality_status = 'VALID' THEN 1 ELSE 0 END) AS pro_valid,
        SUM(CASE WHEN quantity_rescue_method = 'DERIVED_FROM_COST' THEN 1 ELSE 0 END) AS pro_rescued_qty
    FROM fact_procurement
    GROUP BY school_id
)
SELECT
    s.school_id,
    s.school_name,
    s.district,
    (COALESCE(a.att_total, 0) + COALESCE(sc.ass_total, 0) + COALESCE(p.pro_total, 0)) AS total_operational_records,
    (COALESCE(a.att_trusted, 0) + COALESCE(sc.ass_valid, 0) + COALESCE(p.pro_valid, 0)) AS trusted_records,
    (COALESCE(a.att_impossible, 0) + COALESCE(a.att_proxy, 0) + COALESCE(sc.ass_proxy_letter, 0) + COALESCE(p.pro_rescued_qty, 0)) AS flagged_records,
    (COALESCE(a.att_impossible, 0) + COALESCE(a.att_proxy, 0)) AS excluded_from_metrics_count,
    ROUND(
        (COALESCE(a.att_trusted, 0) + COALESCE(sc.ass_valid, 0) + COALESCE(p.pro_valid, 0)) * 100.0 /
        NULLIF(COALESCE(a.att_total, 0) + COALESCE(sc.ass_total, 0) + COALESCE(p.pro_total, 0), 0),
        1
    ) AS data_quality_rate_pct
FROM dim_school s
LEFT JOIN att_q a ON s.school_id = a.school_id
LEFT JOIN ass_q sc ON s.school_id = sc.school_id
LEFT JOIN pro_q p ON s.school_id = p.school_id;

-- ------------------------------------------------------------
-- VIEW 6: school_risk
-- Granularity: One row per school
-- Multi-factor Retention Risk Proxy (45% Att / 35% Acad / 20% Infra)
-- Enforces: 0-100 normalization, dynamic coverage weighting, deterministic bands
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW school_risk AS
WITH base AS (
    SELECT
        p.school_id,
        p.school_name,
        p.district,
        p.block,
        p.enrollment,
        p.attendance_rate,
        p.academic_score,
        w.infrastructure_readiness_pct,
        p.quality_coverage_pct,
        ROUND(GREATEST(0.0, LEAST(100.0, 100.0 - p.attendance_rate)), 1) AS attendance_risk,
        ROUND(GREATEST(0.0, LEAST(100.0, 100.0 - p.academic_score)), 1) AS academic_risk,
        ROUND(GREATEST(0.0, LEAST(100.0, 100.0 - w.infrastructure_readiness_pct)), 1) AS infrastructure_risk
    FROM school_performance p
    JOIN school_welfare w ON p.school_id = w.school_id
),
scored AS (
    SELECT
        *,
        ROUND(0.45 * attendance_risk + 0.35 * academic_risk + 0.20 * infrastructure_risk, 1) AS risk_score,
        CASE
            WHEN attendance_risk >= 50.0 AND academic_risk >= 50.0 AND infrastructure_risk >= 50.0 THEN 'MULTI_FACTOR'
            WHEN attendance_risk >= academic_risk AND attendance_risk >= infrastructure_risk THEN 'ATTENDANCE'
            WHEN academic_risk >= attendance_risk AND academic_risk >= infrastructure_risk THEN 'ACADEMIC'
            ELSE 'INFRASTRUCTURE'
        END AS primary_risk_driver
    FROM base
)
SELECT
    *,
    CASE
        WHEN risk_score >= 75.0 THEN 'CRITICAL'
        WHEN risk_score >= 50.0 THEN 'HIGH'
        WHEN risk_score >= 25.0 THEN 'MODERATE'
        ELSE 'LOW'
    END AS risk_level
FROM scored;

-- ------------------------------------------------------------
-- VIEW 7: school_intervention_priority
-- Granularity: One row per school
-- Combines Risk Severity (60%), Peer Deficit (20%), Multi-Factor (10%), Confidence (10%)
-- Produces deterministic rank ordered by intervention urgency
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW school_intervention_priority AS
WITH base AS (
    SELECT
        r.*,
        d.avg_attendance_rate AS dist_att,
        d.avg_academic_score AS dist_acad,
        d.avg_infrastructure_readiness AS dist_infra
    FROM school_risk r
    LEFT JOIN district_performance d ON r.district = d.district
),
gaps AS (
    SELECT
        *,
        ROUND(attendance_rate - dist_att, 1) AS attendance_gap_vs_district,
        ROUND(academic_score - dist_acad, 1) AS academic_gap_vs_district,
        ROUND(infrastructure_readiness_pct - dist_infra, 1) AS infrastructure_gap_vs_district,
        (
            CASE WHEN (attendance_rate - dist_att) < 0 THEN ABS(attendance_rate - dist_att) * 0.4 ELSE 0 END +
            CASE WHEN (academic_score - dist_acad) < 0 THEN ABS(academic_score - dist_acad) * 0.4 ELSE 0 END +
            CASE WHEN (infrastructure_readiness_pct - dist_infra) < 0 THEN ABS(infrastructure_readiness_pct - dist_infra) * 0.2 ELSE 0 END
        ) AS deficit_penalty
    FROM base
)
SELECT
    school_id,
    school_name,
    district,
    block,
    enrollment,
    attendance_risk,
    academic_risk,
    infrastructure_risk,
    risk_score,
    risk_level,
    primary_risk_driver,
    attendance_gap_vs_district,
    academic_gap_vs_district,
    infrastructure_gap_vs_district,
    ROUND(
        LEAST(100.0,
            (risk_score * 0.60) +
            (LEAST(30.0, deficit_penalty) * 0.67) +
            (CASE WHEN primary_risk_driver = 'MULTI_FACTOR' THEN 10.0 ELSE 0.0 END) +
            (CASE WHEN quality_coverage_pct >= 80.0 THEN 10.0 ELSE 5.0 END)
        ),
        1
    ) AS intervention_priority_score,
    ROW_NUMBER() OVER(
        ORDER BY
            ROUND(LEAST(100.0, (risk_score * 0.60) + (LEAST(30.0, deficit_penalty) * 0.67) + (CASE WHEN primary_risk_driver = 'MULTI_FACTOR' THEN 10.0 ELSE 0.0 END) + (CASE WHEN quality_coverage_pct >= 80.0 THEN 10.0 ELSE 5.0 END)), 1) DESC,
            enrollment DESC,
            school_id ASC
    ) AS intervention_rank
FROM gaps;

-- ------------------------------------------------------------
-- VIEW 8: school_welfare_gap
-- Granularity: One row per school
-- 2x2 Matrix: Infrastructure Readiness (X) vs Academic Performance (Y)
-- Quadrants: MODEL, RESILIENT, ACADEMIC INTERVENTION, CRITICAL INTERVENTION
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW school_welfare_gap AS
SELECT
    p.school_id,
    p.school_name,
    p.district,
    p.block,
    p.enrollment,
    p.attendance_rate,
    p.academic_score,
    w.infrastructure_readiness_pct,
    CASE
        WHEN w.infrastructure_readiness_pct >= 50.0 AND p.academic_score >= 65.0 THEN 'MODEL'
        WHEN w.infrastructure_readiness_pct < 50.0 AND p.academic_score >= 65.0 THEN 'RESILIENT'
        WHEN w.infrastructure_readiness_pct >= 50.0 AND p.academic_score < 65.0 THEN 'ACADEMIC INTERVENTION'
        ELSE 'CRITICAL INTERVENTION'
    END AS welfare_quadrant,
    CASE
        WHEN w.infrastructure_readiness_pct >= 50.0 AND p.academic_score >= 65.0 THEN 'Strong infrastructure support and robust academic learning outcomes'
        WHEN w.infrastructure_readiness_pct < 50.0 AND p.academic_score >= 65.0 THEN 'High academic outcomes achieved despite significant infrastructure constraints'
        WHEN w.infrastructure_readiness_pct >= 50.0 AND p.academic_score < 65.0 THEN 'Adequate physical infrastructure present; learning outcomes lag peer benchmarks'
        ELSE 'Dual deficiency: severely constrained physical infrastructure and low academic scores'
    END AS quadrant_description
FROM school_performance p
JOIN school_welfare w ON p.school_id = w.school_id;

-- ------------------------------------------------------------
-- VIEW 9: district_risk_summary
-- Granularity: One row per district
-- High-level leadership intelligence for cross-district intervention allocation
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW district_risk_summary AS
SELECT
    district,
    COUNT(DISTINCT school_id) AS school_count,
    SUM(enrollment) AS total_enrolled_students,
    SUM(CASE WHEN risk_level = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_school_count,
    SUM(CASE WHEN risk_level IN ('CRITICAL', 'HIGH') THEN 1 ELSE 0 END) AS high_priority_school_count,
    ROUND(SUM(CASE WHEN risk_level IN ('CRITICAL', 'HIGH') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS district_risk_rate_pct,
    ROUND(AVG(risk_score), 1) AS avg_risk_score,
    ROUND(AVG(attendance_rate), 2) AS avg_attendance_rate,
    ROUND(AVG(academic_score), 2) AS avg_academic_score,
    ROUND(AVG(infrastructure_readiness_pct), 1) AS avg_infrastructure_readiness,
    ROUND(AVG(quality_coverage_pct), 1) AS data_quality_coverage_pct
FROM school_risk
GROUP BY district
ORDER BY district_risk_rate_pct DESC, avg_risk_score DESC;

-- ------------------------------------------------------------
-- VIEW 10: procurement_anomalies
-- Granularity: One row per school
-- Peer IQR Benchmarked Spend & Volume Anomaly Detection
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW procurement_anomalies AS
WITH stats AS (
    SELECT
        QUANTILE_CONT(avg_cost_per_student, 0.25) AS q1,
        QUANTILE_CONT(avg_cost_per_student, 0.75) AS q3
    FROM procurement_summary
),
cutoffs AS (
    SELECT
        q1,
        q3,
        (q3 + 1.5 * (q3 - q1)) AS upper_iqr_threshold
    FROM stats
)
SELECT
    p.school_id,
    p.school_name,
    p.district,
    p.enrollment,
    p.avg_cost_per_student,
    p.avg_cost_per_kg,
    p.total_spend_inr,
    CASE
        WHEN p.avg_cost_per_student > c.upper_iqr_threshold THEN TRUE
        WHEN p.avg_cost_per_kg > 115.0 THEN TRUE
        ELSE FALSE
    END AS is_procurement_outlier,
    CASE
        WHEN p.avg_cost_per_student > c.upper_iqr_threshold THEN 'Spend per student (₹' || CAST(ROUND(p.avg_cost_per_student, 1) AS VARCHAR) || ') exceeds peer 75th percentile + 1.5 IQR threshold (₹' || CAST(ROUND(c.upper_iqr_threshold, 1) AS VARCHAR) || ')'
        WHEN p.avg_cost_per_kg > 115.0 THEN 'Average cost per kg (₹' || CAST(ROUND(p.avg_cost_per_kg, 1) AS VARCHAR) || ') is heavily skewed towards high-cost cooking oil relative to peer mix'
        ELSE 'Within standard peer distribution'
    END AS procurement_anomaly_reason
FROM procurement_summary p
CROSS JOIN cutoffs c;

