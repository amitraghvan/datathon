"""Phase 4 Analytics & Risk Intelligence Pipeline.

Orchestrates:
1. Multi-factor Retention Risk & Intervention Priority generation
2. School Segmentation (K-Means with Silhouette Validation)
3. Welfare Gap 2x2 Matrix
4. Attendance-Academic Association Analysis
5. Sensitivity Analyses (Weights & Letter Grades)
6. Peer-Benchmarked Procurement Anomaly Detection
7. Materialization of Analytical Parquet Tables and Summary Report
"""

import json
import time
from typing import Any, Dict

import pandas as pd

from src.analytics.advanced import (
    analyze_attendance_academic_association,
    calculate_welfare_gap_matrix,
    detect_procurement_outliers,
    run_letter_grade_sensitivity_analysis,
    run_risk_weight_sensitivity_analysis,
)
from src.analytics.risk import calculate_school_risk
from src.analytics.segmentation import perform_school_segmentation
from src.config import PROCESSED_DATA_DIR, logger
from src.modeling.database import get_db_connection


def run_phase4_analytics() -> Dict[str, Any]:
    """Execute end-to-end Phase 4 analytics suite and materialize analytical marts."""
    start_time = time.time()
    logger.info("Executing Phase 4 Analytics & Risk Intelligence pipeline...")

    # 1. School Risk & Intervention Priority
    df_risk = calculate_school_risk()
    risk_parquet = PROCESSED_DATA_DIR / "school_risk.parquet"
    df_risk.to_parquet(risk_parquet, index=False)
    logger.info("Materialized %s (%d rows)", risk_parquet.name, len(df_risk))

    df_prio = df_risk.sort_values(
        by=["intervention_priority_score", "enrollment", "school_id"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    prio_parquet = PROCESSED_DATA_DIR / "school_intervention_priority.parquet"
    df_prio.to_parquet(prio_parquet, index=False)
    logger.info("Materialized %s (%d rows)", prio_parquet.name, len(df_prio))

    # 2. School Segmentation (K=4, random_state=42)
    df_seg, seg_eval = perform_school_segmentation(k_clusters=4, random_state=42)
    seg_parquet = PROCESSED_DATA_DIR / "school_segmentation.parquet"
    df_seg.to_parquet(seg_parquet, index=False)
    logger.info(
        "Materialized %s (%d rows, Silhouette=%.3f)",
        seg_parquet.name,
        len(df_seg),
        seg_eval["silhouette_score"],
    )

    # 3. Welfare Gap Matrix
    df_gap = calculate_welfare_gap_matrix()
    gap_parquet = PROCESSED_DATA_DIR / "school_welfare_gap.parquet"
    df_gap.to_parquet(gap_parquet, index=False)
    logger.info("Materialized %s (%d rows)", gap_parquet.name, len(df_gap))

    # 4. District Risk Summary
    con = get_db_connection(read_only=True)
    try:
        df_dist = con.execute("SELECT * FROM district_risk_summary;").df()
    finally:
        con.close()
    dist_parquet = PROCESSED_DATA_DIR / "district_risk_summary.parquet"
    df_dist.to_parquet(dist_parquet, index=False)
    logger.info("Materialized %s (%d rows)", dist_parquet.name, len(df_dist))

    # 5. Attendance-Academic Association
    assoc_data = analyze_attendance_academic_association()
    df_assoc_dist = pd.DataFrame(assoc_data["district_breakdown"])
    assoc_parquet = PROCESSED_DATA_DIR / "attendance_academic_association.parquet"
    df_assoc_dist.to_parquet(assoc_parquet, index=False)
    logger.info("Materialized %s (%d district records)", assoc_parquet.name, len(df_assoc_dist))

    # 6. Procurement Anomalies
    df_proc_anom = detect_procurement_outliers()
    proc_parquet = PROCESSED_DATA_DIR / "procurement_anomalies.parquet"
    df_proc_anom.to_parquet(proc_parquet, index=False)
    logger.info(
        "Materialized %s (%d rows, %d anomalies)",
        proc_parquet.name,
        len(df_proc_anom),
        df_proc_anom["is_procurement_outlier"].sum(),
    )

    # 7. Sensitivity Analyses
    sens_weights = run_risk_weight_sensitivity_analysis()
    sens_letters = run_letter_grade_sensitivity_analysis()

    # 8. Register Tables in DuckDB
    con = get_db_connection(read_only=False)
    try:
        con.execute(
            f"CREATE OR REPLACE TABLE school_segmentation AS SELECT * FROM read_parquet('{seg_parquet}');"
        )
        con.execute(
            f"CREATE OR REPLACE TABLE attendance_academic_association AS SELECT * FROM read_parquet('{assoc_parquet}');"
        )
        logger.info(
            "Registered school_segmentation and attendance_academic_association tables in DuckDB."
        )
    finally:
        con.close()

    elapsed = round(time.time() - start_time, 2)
    logger.info("Phase 4 Analytics completed in %ss", elapsed)

    # 9. Structured Summary
    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": elapsed,
        "school_count": len(df_risk),
        "risk_distribution": df_risk["risk_level"].value_counts().to_dict(),
        "primary_drivers_distribution": df_risk["primary_risk_driver"].value_counts().to_dict(),
        "top_5_priority_schools": df_prio.head(5)[
            [
                "school_id",
                "school_name",
                "district",
                "risk_score",
                "intervention_priority_score",
                "primary_risk_driver",
                "recommended_intervention",
            ]
        ].to_dict(orient="records"),
        "welfare_quadrants_distribution": df_gap["welfare_quadrant"].value_counts().to_dict(),
        "association_analysis": {
            "sample_size": assoc_data["sample_size"],
            "pearson_r": assoc_data["pearson_r"],
            "spearman_rho": assoc_data["spearman_rho"],
            "strength": assoc_data["association_strength"],
            "causal_disclaimer": "Analytical correlation only; does not claim causality.",
        },
        "segmentation_evaluation": {
            "k_selected": seg_eval["k_selected"],
            "silhouette_score": seg_eval["silhouette_score"],
            "k_candidates_silhouette": seg_eval["k_candidates_silhouette"],
            "cluster_profiles": seg_eval["cluster_profiles"],
        },
        "weight_sensitivity": {
            "overall_stability": sens_weights["overall_stability"],
            "scenario_evaluations": sens_weights["scenario_evaluations"],
        },
        "letter_grade_sensitivity": {
            "pearson_correlation": sens_letters["pearson_correlation"],
            "spearman_rank_correlation": sens_letters["spearman_rank_correlation"],
            "district_rank_correlation": sens_letters["district_rank_correlation"],
            "mean_risk_score_impact": sens_letters["mean_risk_score_impact"],
            "is_stable": sens_letters["is_stable"],
        },
        "procurement_anomalies": {
            "total_schools_evaluated": len(df_proc_anom),
            "outlier_count": int(df_proc_anom["is_procurement_outlier"].sum()),
        },
    }

    summary_path = PROCESSED_DATA_DIR / "phase4_analytics_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    logger.info("Saved Phase 4 Analytics summary to %s", summary_path)

    return summary


if __name__ == "__main__":
    summary = run_phase4_analytics()
    print("Phase 4 Analytics Suite executed successfully.")
    print("Risk distribution:", summary["risk_distribution"])
    print(
        "Top priority school:",
        summary["top_5_priority_schools"][0]["school_name"],
        summary["top_5_priority_schools"][0]["intervention_priority_score"],
    )
