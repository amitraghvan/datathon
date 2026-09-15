"""Centralized, governed SQL queries matching canonical DuckDB warehouse views."""

SCHOOL_MASTER_ENRICHED_SQL = """
SELECT
    s.school_id,
    s.school_name,
    s.district,
    s.block,
    s.school_type,
    s.medium,
    s.total_enrolled_students AS enrollment,
    COALESCE(p.attendance_rate, 0.0) AS attendance_rate_pct,
    COALESCE(p.academic_score, 0.0) AS academic_score,
    0.0 AS student_teacher_ratio,
    COALESCE(p.attendance_records, 0) AS total_attendance_records,
    COALESCE(p.assessment_records, 0) AS assessments_count,
    COALESCE(w.infrastructure_readiness_pct, 0.0) AS infrastructure_readiness_pct,
    CASE WHEN w.electricity_status = 'TRUE' THEN TRUE WHEN w.electricity_status = 'FALSE' THEN FALSE ELSE NULL END AS electricity,
    CASE WHEN w.water_status = 'TRUE' THEN TRUE WHEN w.water_status = 'FALSE' THEN FALSE ELSE NULL END AS drinking_water,
    CASE WHEN w.toilet_status = 'TRUE' THEN TRUE WHEN w.toilet_status = 'FALSE' THEN FALSE ELSE NULL END AS functional_toilet,
    CASE WHEN w.boundary_status = 'TRUE' THEN TRUE WHEN w.boundary_status = 'FALSE' THEN FALSE ELSE NULL END AS boundary_wall,
    CASE WHEN w.playground_status = 'TRUE' THEN TRUE WHEN w.playground_status = 'FALSE' THEN FALSE ELSE NULL END AS playground,
    COALESCE(r.risk_score, 0.0) AS risk_score,
    COALESCE(r.risk_level, 'LOW') AS risk_tier,
    COALESCE(r.primary_risk_driver, 'Multi-factor') AS primary_driver,
    'None' AS secondary_driver,
    COALESCE(r.attendance_risk, 0.0) AS attendance_deficit,
    COALESCE(r.academic_risk, 0.0) AS academic_deficit,
    COALESCE(r.infrastructure_risk, 0.0) AS infrastructure_deficit,
    COALESCE(p.quality_coverage_pct, 100.0) AS data_coverage_score,
    100.0 AS confidence_score,
    COALESCE(i.intervention_priority_score, 0.0) AS intervention_priority_score,
    CASE
        WHEN COALESCE(i.intervention_priority_score, 0.0) >= 45.0 THEN 'HIGH'
        WHEN COALESCE(i.intervention_priority_score, 0.0) >= 35.0 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS intervention_priority_tier,
    COALESCE(wg.welfare_quadrant, 'MODEL') AS welfare_quadrant,
    wg.quadrant_description AS quadrant_action,
    COALESCE(dq.data_quality_rate_pct, 94.6) AS data_quality_rate_pct
FROM dim_school s
LEFT JOIN school_performance p ON s.school_id = p.school_id
LEFT JOIN school_welfare w ON s.school_id = w.school_id
LEFT JOIN school_risk r ON s.school_id = r.school_id
LEFT JOIN school_intervention_priority i ON s.school_id = i.school_id
LEFT JOIN school_welfare_gap wg ON s.school_id = wg.school_id
LEFT JOIN school_data_quality dq ON s.school_id = dq.school_id
"""

DISTRICT_SUMMARY_SQL = """
SELECT
    d.district,
    d.school_count,
    d.total_enrolled_students AS total_enrollment,
    d.avg_attendance_rate,
    d.avg_academic_score,
    d.avg_infrastructure_readiness,
    d.data_quality_coverage_pct AS avg_data_quality_rate,
    COALESCE(dr.high_priority_school_count, 0) AS high_priority_school_count,
    0 AS moderate_priority_school_count,
    COALESCE(dr.critical_school_count, 0) AS critical_quadrant_school_count,
    ROUND(CAST(COALESCE(dr.high_priority_school_count, 0) AS DOUBLE) / NULLIF(d.school_count, 0) * 100.0, 1) AS priority_school_rate_pct
FROM district_performance d
LEFT JOIN district_risk_summary dr ON d.district = dr.district
ORDER BY d.district ASC
"""

PROCUREMENT_ENRICHED_SQL = """
SELECT
    p.school_id,
    p.school_name,
    p.district,
    p.total_spend_inr,
    p.total_quantity_kg,
    p.procurement_records,
    p.avg_cost_per_kg,
    p.avg_cost_per_student,
    p.grain_count,
    p.vendor_count,
    COALESCE(a.is_procurement_outlier, FALSE) AS is_procurement_outlier,
    350.0 AS spend_per_student_iqr_threshold,
    a.procurement_anomaly_reason,
    p.enrollment
FROM procurement_summary p
LEFT JOIN procurement_anomalies a ON p.school_id = a.school_id
ORDER BY p.total_spend_inr DESC
"""

DATA_QUALITY_OVERVIEW_SQL = """
SELECT
    COUNT(*) AS total_schools,
    SUM(total_operational_records) AS total_operational_records,
    SUM(trusted_records) AS trusted_records,
    SUM(flagged_records) AS flagged_records,
    SUM(excluded_from_metrics_count) AS excluded_from_metrics_count,
    ROUND(AVG(data_quality_rate_pct), 1) AS data_quality_rate_pct
FROM school_data_quality
"""

ELECTRICITY_IMPACT_ANALYSIS_SQL = """
SELECT
    w.electricity_status AS electricity,
    COUNT(DISTINCT s.school_id) AS school_count,
    ROUND(AVG(p.academic_score), 1) AS avg_academic_score,
    ROUND(AVG(p.attendance_rate), 1) AS avg_attendance_rate,
    ROUND(AVG(p.assessment_records), 0) AS avg_assessments_per_school,
    ROUND(AVG(p.quality_coverage_pct), 1) AS avg_data_coverage_score
FROM dim_school s
JOIN school_welfare w ON s.school_id = w.school_id
JOIN school_performance p ON s.school_id = p.school_id
GROUP BY w.electricity_status
ORDER BY w.electricity_status DESC
"""

SCHOOL_ATTENDANCE_SERIES_SQL = """
SELECT
    date,
    SUM(present_students) AS present,
    SUM(total_students) AS total,
    ROUND(SUM(present_students) * 100.0 / NULLIF(SUM(total_students), 0), 1) AS attendance_pct,
    COUNT(*) AS records_count,
    BOOL_OR(quality_status = 'FLAGGED') AS has_flagged_record,
    BOOL_OR(is_proxy_attendance = TRUE) AS has_proxy_record
FROM fact_attendance
WHERE school_id = ?
GROUP BY date
ORDER BY date ASC
"""

SCHOOL_ASSESSMENT_DETAILS_SQL = """
SELECT
    a.subject_standard AS subject,
    a.grade_number AS grade,
    ROUND(AVG(a.normalized_score_pct), 1) AS avg_score,
    COUNT(*) AS assessment_count,
    ROUND(AVG(COALESCE(a.total_students_assessed, 0)), 0) AS avg_total_marks,
    BOOL_OR(a.is_letter_grade_proxy = TRUE) AS has_proxy_score
FROM fact_assessment a
WHERE a.school_id = ?
GROUP BY a.subject_standard, a.grade_number
ORDER BY a.subject_standard, a.grade_number
"""
