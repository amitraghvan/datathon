"""Retention & Intervention Intelligence Engine for EduPulse AI.

Implements:
1. Multi-factor Intervention Priority Score & Retention Risk Proxy.
2. Transparent component decomposition: Attendance Risk (45%), Academic Risk (35%), Infrastructure Risk (20%).
3. Coverage-aware scoring with dynamic weight re-normalization (prevents missing data from fabricating risk).
4. Deterministic risk driver ranking & intervention recommendations.
5. District benchmark gap analysis.
"""

from typing import Optional

import duckdb
import pandas as pd

from src.config import RISK_TIERS, RISK_WEIGHTS, logger
from src.modeling.database import get_db_connection


def classify_risk_level(score: Optional[float]) -> str:
    """Classify risk score into configured bands."""
    if score is None or pd.isna(score):
        return "UNKNOWN"
    for level, (low, high) in RISK_TIERS.items():
        if low <= score < high or (level == "CRITICAL" and score >= high):
            return level
    return "CRITICAL" if score >= 100.0 else "LOW"


def get_recommended_intervention(risk_level: str, primary_driver: str) -> str:
    """Deterministic, transparent mapping from risk level and drivers to action."""
    if risk_level == "CRITICAL":
        if primary_driver == "MULTI_FACTOR":
            return "Deploy multi-factor emergency taskforce (attendance counseling + remedial FLN + urgent toilet/water repairs)"
        elif primary_driver == "ATTENDANCE":
            return (
                "Immediate community-level attendance outreach, parent engagement, and proxy audit"
            )
        elif primary_driver == "ACADEMIC":
            return "Intensive FLN foundational literacy & numeracy remediation bootcamp"
        elif primary_driver == "INFRASTRUCTURE":
            return "Expedited civil infrastructure repair grant for essential amenities"
        return "Priority administrative inspection and comprehensive student retention plan"
    elif risk_level == "HIGH":
        if primary_driver == "ATTENDANCE":
            return "Targeted attendance tracking, SMS alerts to parents, and student mentorship"
        elif primary_driver == "ACADEMIC":
            return "Subject-specific after-school remedial tutoring in Math and Languages"
        elif primary_driver == "INFRASTRUCTURE":
            return "School sanitation and electricity maintenance work order"
        return "Targeted multi-domain intervention and monthly progress review"
    elif risk_level == "MODERATE":
        return "Preventative monitoring, quarterly academic check-ins, and routine facility audits"
    else:
        return "Routine monitoring and peer-mentorship school modeling"


def calculate_school_risk(con: Optional[duckdb.DuckDBPyConnection] = None) -> pd.DataFrame:
    """Calculate comprehensive, coverage-aware intervention risk proxy for all schools.

    Queries governed DuckDB analytical views:
    - school_performance
    - school_welfare
    - district_performance
    """
    should_close = False
    if con is None:
        con = get_db_connection(read_only=True)
        should_close = True

    try:
        query = """
        SELECT
            p.school_id,
            p.school_name,
            p.district,
            p.block,
            p.enrollment,
            p.school_type,
            p.medium,
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
            d.avg_attendance_rate AS district_avg_attendance,
            d.avg_academic_score AS district_avg_academic,
            d.avg_infrastructure_readiness AS district_avg_infra
        FROM school_performance p
        LEFT JOIN school_welfare w ON p.school_id = w.school_id
        LEFT JOIN district_performance d ON p.district = d.district
        ORDER BY p.school_id;
        """
        df = con.execute(query).df()
    finally:
        if should_close:
            con.close()

    # Also extract numeric-only academic scores for sensitivity analysis
    con_sens = get_db_connection(read_only=True)
    try:
        num_score_query = """
        SELECT
            school_id,
            ROUND(
                SUM(CASE WHEN quality_status = 'VALID' AND NOT is_letter_grade_proxy THEN normalized_score_pct * total_students_assessed ELSE 0 END) /
                NULLIF(SUM(CASE WHEN quality_status = 'VALID' AND NOT is_letter_grade_proxy THEN total_students_assessed ELSE 0 END), 0),
                2
            ) AS numeric_only_academic_score
        FROM fact_assessment
        GROUP BY school_id;
        """
        df_num_scores = con_sens.execute(num_score_query).df()
    finally:
        con_sens.close()

    df = df.merge(df_num_scores, on="school_id", how="left")

    records = []
    w_att_base = RISK_WEIGHTS["attendance"]
    w_acad_base = RISK_WEIGHTS["academics"]
    w_infra_base = RISK_WEIGHTS["infrastructure"]

    for _, row in df.iterrows():
        sid = row["school_id"]

        # ---------------------------------------------------------
        # 1. ATTENDANCE RISK COMPONENT (0-100)
        # ---------------------------------------------------------
        att_rate = row["attendance_rate"]
        att_recs = row["attendance_records"]
        if pd.notna(att_rate) and att_recs > 0:
            att_risk = max(0.0, min(100.0, 100.0 - float(att_rate)))
            att_status = (
                "SUFFICIENT"
                if att_recs >= 25
                else ("LIMITED" if att_recs >= 10 else "INSUFFICIENT")
            )
            att_cov = min(100.0, round((att_recs / 30.0) * 100.0, 1))
        else:
            att_risk = None
            att_status = "MISSING"
            att_cov = 0.0

        # ---------------------------------------------------------
        # 2. ACADEMIC RISK COMPONENT (0-100)
        # ---------------------------------------------------------
        acad_score = row["academic_score"]
        ass_recs = row["assessment_records"]
        num_only_score = row["numeric_only_academic_score"]

        if pd.notna(acad_score) and ass_recs > 0:
            acad_risk = max(0.0, min(100.0, 100.0 - float(acad_score)))
            acad_status = (
                "SUFFICIENT" if ass_recs >= 10 else ("LIMITED" if ass_recs >= 4 else "INSUFFICIENT")
            )
            acad_cov = min(100.0, round((ass_recs / 12.0) * 100.0, 1))
        else:
            acad_risk = None
            acad_status = "MISSING"
            acad_cov = 0.0

        # ---------------------------------------------------------
        # 3. INFRASTRUCTURE RISK COMPONENT (0-100)
        # ---------------------------------------------------------
        infra_readiness = row["infrastructure_readiness_pct"]
        amenities = [
            row["electricity_status"],
            row["water_status"],
            row["toilet_status"],
            row["boundary_status"],
            row["playground_status"],
        ]
        known_count = sum(1 for a in amenities if a in ("TRUE", "FALSE"))
        unknown_count = sum(1 for a in amenities if a == "UNKNOWN")
        infra_cov = round((known_count / 5.0) * 100.0, 1)

        if pd.notna(infra_readiness) and known_count > 0:
            infra_risk = max(0.0, min(100.0, 100.0 - float(infra_readiness)))
            infra_status = (
                "SUFFICIENT"
                if infra_cov >= 80.0
                else ("LIMITED" if infra_cov >= 40.0 else "INSUFFICIENT")
            )
        else:
            infra_risk = None
            infra_status = "MISSING"

        # ---------------------------------------------------------
        # 4. COVERAGE-AWARE RISK SCORE CALCULATION
        # ---------------------------------------------------------
        valid_components = []
        if att_risk is not None:
            valid_components.append(("att", att_risk, w_att_base))
        if acad_risk is not None:
            valid_components.append(("acad", acad_risk, w_acad_base))
        if infra_risk is not None:
            valid_components.append(("infra", infra_risk, w_infra_base))

        if len(valid_components) >= 2:
            sum_weights = sum(c[2] for c in valid_components)
            # Dynamic re-normalization of weights if any component is missing
            risk_score = round(sum(c[1] * (c[2] / sum_weights) for c in valid_components), 1)
            risk_status = "COMPUTED"
        else:
            risk_score = None
            risk_status = "INSUFFICIENT_DATA"

        # Overall composite coverage (0-100%)
        risk_coverage = round((att_cov * 0.45) + (acad_cov * 0.35) + (infra_cov * 0.20), 1)
        risk_level = classify_risk_level(risk_score)

        # ---------------------------------------------------------
        # 5. RISK DRIVER RANKING & TAXONOMY
        # ---------------------------------------------------------
        driver_contributions = []
        if att_risk is not None:
            driver_contributions.append(("ATTENDANCE", att_risk, round(att_risk * w_att_base, 1)))
        if acad_risk is not None:
            driver_contributions.append(("ACADEMIC", acad_risk, round(acad_risk * w_acad_base, 1)))
        if infra_risk is not None:
            driver_contributions.append(
                ("INFRASTRUCTURE", infra_risk, round(infra_risk * w_infra_base, 1))
            )

        driver_contributions.sort(key=lambda x: x[1], reverse=True)

        if (
            att_risk is not None
            and att_risk >= 50.0
            and acad_risk is not None
            and acad_risk >= 50.0
            and infra_risk is not None
            and infra_risk >= 50.0
        ):
            primary_driver = "MULTI_FACTOR"
            secondary_driver = driver_contributions[0][0] if driver_contributions else "NONE"
        elif driver_contributions:
            primary_driver = driver_contributions[0][0]
            secondary_driver = (
                driver_contributions[1][0] if len(driver_contributions) > 1 else "NONE"
            )
        else:
            primary_driver = "DATA_INSUFFICIENT"
            secondary_driver = "NONE"

        recommended_action = get_recommended_intervention(risk_level, primary_driver)

        # ---------------------------------------------------------
        # 6. DISTRICT BENCHMARK GAP ANALYSIS
        # ---------------------------------------------------------
        dist_att = row["district_avg_attendance"] or 0.0
        dist_acad = row["district_avg_academic"] or 0.0
        dist_infra = row["district_avg_infra"] or 0.0

        att_gap = round(att_rate - dist_att, 1) if pd.notna(att_rate) else 0.0
        acad_gap = round(acad_score - dist_acad, 1) if pd.notna(acad_score) else 0.0
        infra_gap = round(infra_readiness - dist_infra, 1) if pd.notna(infra_readiness) else 0.0

        # Benchmark deficit indicator (penalizes falling below district peers)
        deficit_penalty = 0.0
        if att_gap < 0:
            deficit_penalty += abs(att_gap) * 0.4
        if acad_gap < 0:
            deficit_penalty += abs(acad_gap) * 0.4
        if infra_gap < 0:
            deficit_penalty += abs(infra_gap) * 0.2

        # ---------------------------------------------------------
        # 7. INTERVENTION PRIORITY SCORE
        # Combines Risk Severity (60%), Peer Deficit (20%), Multi-Factor Flag (10%), Confidence (10%)
        # ---------------------------------------------------------
        if risk_score is not None:
            multi_factor_boost = 10.0 if primary_driver == "MULTI_FACTOR" else 0.0
            confidence_boost = 10.0 if risk_coverage >= 80.0 else 5.0
            raw_priority = (
                (risk_score * 0.60)
                + (min(30.0, deficit_penalty) * 0.67)  # Scaled to max ~20 pts
                + multi_factor_boost
                + confidence_boost
            )
            intervention_priority_score = min(100.0, round(raw_priority, 1))
        else:
            intervention_priority_score = 0.0

        records.append(
            {
                "school_id": sid,
                "school_name": row["school_name"],
                "district": row["district"],
                "block": row["block"],
                "enrollment": row["enrollment"],
                "school_type": row["school_type"],
                "medium": row["medium"],
                # Component Risks
                "attendance_risk": att_risk,
                "academic_risk": acad_risk,
                "infrastructure_risk": infra_risk,
                # Component Coverages & Status
                "attendance_status": att_status,
                "academic_status": acad_status,
                "infrastructure_status": infra_status,
                "known_amenity_count": known_count,
                "unknown_amenity_count": unknown_count,
                "attendance_coverage_pct": att_cov,
                "academic_coverage_pct": acad_cov,
                "infrastructure_coverage_pct": infra_cov,
                # Overall Risk
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_status": risk_status,
                "risk_data_coverage_pct": risk_coverage,
                # Drivers & Actions
                "primary_risk_driver": primary_driver,
                "secondary_risk_driver": secondary_driver,
                "recommended_intervention": recommended_action,
                # District Benchmarks
                "attendance_gap_vs_district": att_gap,
                "academic_gap_vs_district": acad_gap,
                "infrastructure_gap_vs_district": infra_gap,
                # Intervention Priority
                "intervention_priority_score": intervention_priority_score,
                # Sensitivity Metrics
                "numeric_only_academic_score": num_only_score,
            }
        )

    df_out = pd.DataFrame(records)

    # Calculate deterministic rank based on priority score, broken by enrollment descending and school_id
    df_out = df_out.sort_values(
        by=["intervention_priority_score", "enrollment", "school_id"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    df_out["intervention_rank"] = range(1, len(df_out) + 1)

    logger.info(
        "Computed risk intelligence for %d schools. Critical count: %d",
        len(df_out),
        (df_out["risk_level"] == "CRITICAL").sum(),
    )
    return df_out
