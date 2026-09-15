"""Governed SQL Query definitions for the EduPulse AI Data Access Layer.

Queries compile directly against canonical DuckDB views and fact/dimension tables.
"""

SCHOOL_MASTER_ENRICHED_SQL = """
SELECT
    s.school_id,
    s.school_name,
    s.district,
    s.block,
    s.total_enrolled_students AS enrollment,
    s.school_type,
    s.medium,
    s.district_imputation_status,
    p.attendance_rate,
    p.academic_score,
    p.attendance_records,
    p.assessment_records,
    p.quality_coverage_pct,
    w.electricity_status,
    w.water_status,
    w.toilet_status,
    w.boundary_status,
    w.playground_status,
    w.infrastructure_readiness_pct,
    w.latest_remarks,
    r.attendance_risk,
    r.academic_risk,
    r.infrastructure_risk,
    r.risk_score,
    r.risk_level,
    r.primary_risk_driver,
    ip.intervention_priority_score,
    ip.intervention_rank,
    ip.attendance_gap_vs_district,
    ip.academic_gap_vs_district,
    ip.infrastructure_gap_vs_district,
    wg.welfare_quadrant,
    wg.quadrant_description
FROM dim_school s
LEFT JOIN school_performance p ON s.school_id = p.school_id
LEFT JOIN school_welfare w ON s.school_id = w.school_id
LEFT JOIN school_risk r ON s.school_id = r.school_id
LEFT JOIN school_intervention_priority ip ON s.school_id = ip.school_id
LEFT JOIN school_welfare_gap wg ON s.school_id = wg.school_id
"""

DISTRICT_SUMMARY_SQL = """
SELECT
    dp.district,
    dp.school_count,
    dp.total_enrolled_students,
    dp.avg_attendance_rate,
    dp.avg_academic_score,
    dp.avg_infrastructure_readiness,
    dp.high_quality_school_count,
    dp.data_quality_coverage_pct,
    dr.critical_school_count,
    dr.high_priority_school_count,
    dr.district_risk_rate_pct,
    dr.avg_risk_score
FROM district_performance dp
LEFT JOIN district_risk_summary dr ON dp.district = dr.district
ORDER BY dr.district_risk_rate_pct DESC, dp.total_enrolled_students DESC;
"""

PROCUREMENT_ENRICHED_SQL = """
SELECT
    ps.school_id,
    ps.school_name,
    ps.district,
    ps.block,
    ps.enrollment,
    ps.procurement_records,
    ps.total_quantity_kg,
    ps.total_spend_inr,
    ps.avg_cost_per_kg,
    ps.avg_cost_per_student,
    ps.avg_kg_per_student,
    ps.grain_count,
    ps.vendor_count,
    ps.rice_kg,
    ps.wheat_kg,
    ps.pulses_kg,
    ps.oil_kg,
    pa.is_procurement_outlier,
    pa.procurement_anomaly_reason
FROM procurement_summary ps
LEFT JOIN procurement_anomalies pa ON ps.school_id = pa.school_id
"""

DATA_QUALITY_OVERVIEW_SQL = """
SELECT
    dq.school_id,
    dq.school_name,
    dq.district,
    dq.total_operational_records,
    dq.trusted_records,
    dq.flagged_records,
    dq.excluded_from_metrics_count,
    dq.data_quality_rate_pct
FROM school_data_quality dq
"""

SCHOOL_ATTENDANCE_SERIES_SQL = """
SELECT
    record_id,
    school_id,
    date,
    grade_number,
    total_students,
    present_students,
    attendance_rate,
    teacher_present,
    is_impossible_attendance,
    is_proxy_attendance,
    is_trusted_attendance,
    quality_status,
    attendance_anomaly_reason
FROM fact_attendance
WHERE school_id = ?
ORDER BY date ASC, grade_number ASC;
"""

SCHOOL_ASSESSMENT_DETAILS_SQL = """
SELECT
    assessment_id,
    school_id,
    date,
    grade_number,
    subject_standard,
    grading_scale,
    normalized_score_pct,
    score_normalization_method,
    is_letter_grade_proxy,
    total_students_assessed,
    quality_status
FROM fact_assessment
WHERE school_id = ?
ORDER BY date ASC, grade_number ASC, subject_standard ASC;
"""

ELECTRICITY_IMPACT_ANALYSIS_SQL = """
SELECT
    w.electricity_status,
    COUNT(DISTINCT s.school_id) AS school_count,
    SUM(s.total_enrolled_students) AS total_enrolled,
    ROUND(AVG(p.academic_score), 2) AS avg_academic_score,
    ROUND(AVG(p.attendance_rate), 2) AS avg_attendance_rate,
    ROUND(AVG(p.quality_coverage_pct), 1) AS data_quality_coverage_pct
FROM dim_school s
JOIN school_welfare w ON s.school_id = w.school_id
JOIN school_performance p ON s.school_id = p.school_id
GROUP BY w.electricity_status
ORDER BY avg_academic_score DESC;
"""
