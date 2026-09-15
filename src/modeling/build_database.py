"""Build canonical star-schema dimensional warehouse in DuckDB from clean Parquet data.

Populates:
- Dimensions: dim_school, dim_date, dim_grade, dim_subject, dim_vendor, dim_grain
- Facts: fact_attendance, fact_assessment, fact_infrastructure, fact_procurement
- Analytical Views: school_performance, school_welfare, district_performance, procurement_summary, school_data_quality
"""

import json
import time
from pathlib import Path
from typing import Any, Dict

from src.config import BASE_DIR, DUCKDB_PATH, PROCESSED_DATA_DIR, logger
from src.modeling.database import execute_sql_file, get_db_connection

SCHEMA_SQL_PATH = BASE_DIR / "src" / "sql" / "schema.sql"
VIEWS_SQL_PATH = BASE_DIR / "src" / "sql" / "views.sql"


def build_canonical_database(db_path: Path | None = None) -> Dict[str, Any]:
    """Execute end-to-end dimensional warehouse build in DuckDB."""
    start_time = time.time()
    target_db = db_path or DUCKDB_PATH
    logger.info("Building canonical DuckDB data mart at %s", target_db)

    # If database file exists, remove to ensure clean rebuild
    if target_db.exists():
        try:
            target_db.unlink()
            logger.info("Removed existing database file for clean rebuild: %s", target_db)
        except Exception as e:
            logger.warning("Could not unlink existing db (%s); rebuilding in-place", e)

    con = get_db_connection(target_db, read_only=False)

    try:
        # 1. Execute DDL Schema
        execute_sql_file(con, SCHEMA_SQL_PATH)

        # 2. Register Processed Parquet Views
        parquet_files = {
            "p_schools": PROCESSED_DATA_DIR / "schools_clean.parquet",
            "p_attendance": PROCESSED_DATA_DIR / "attendance_clean.parquet",
            "p_infrastructure": PROCESSED_DATA_DIR / "infrastructure_clean.parquet",
            "p_procurement": PROCESSED_DATA_DIR / "procurement_clean.parquet",
            "p_assessments": PROCESSED_DATA_DIR / "assessments_clean.parquet",
        }

        for view_name, p_path in parquet_files.items():
            if not p_path.exists():
                raise FileNotFoundError(f"Required Parquet file missing: {p_path}")
            con.execute(
                f"CREATE OR REPLACE TEMPORARY VIEW {view_name} AS SELECT * FROM read_parquet('{p_path}');"
            )

        # -------------------------------------------------------------
        # 3. POPULATE DIMENSIONS
        # -------------------------------------------------------------
        logger.info("Populating dimensions...")

        # dim_school
        con.execute("""
            INSERT INTO dim_school
            SELECT
                ROW_NUMBER() OVER(ORDER BY school_id) AS school_key,
                school_id,
                school_name,
                district,
                block,
                total_enrolled_students,
                school_type,
                medium,
                district_imputation_status
            FROM p_schools;
        """)

        # dim_date
        con.execute("""
            INSERT INTO dim_date
            WITH all_distinct_dates AS (
                SELECT DISTINCT CAST(date AS DATE) AS d FROM p_attendance WHERE date IS NOT NULL
                UNION
                SELECT DISTINCT CAST(date AS DATE) AS d FROM p_infrastructure WHERE date IS NOT NULL
                UNION
                SELECT DISTINCT CAST(date AS DATE) AS d FROM p_procurement WHERE date IS NOT NULL
                UNION
                SELECT DISTINCT CAST(date AS DATE) AS d FROM p_assessments WHERE date IS NOT NULL
            )
            SELECT
                CAST(strftime(d, '%Y%m%d') AS INTEGER) AS date_key,
                d AS date,
                year(d) AS year,
                month(d) AS month,
                strftime(d, '%B') AS month_name,
                CAST(((month(d) - 1) / 3) + 1 AS INTEGER) AS quarter,
                CAST(strftime(d, '%W') AS INTEGER) AS week,
                strftime(d, '%A') AS day_of_week,
                strftime(d, '%a') AS day_name,
                (dayofweek(d) IN (0, 6)) AS is_weekend,
                (dayofweek(d) = 0) AS is_sunday,
                (day(d) = 1) AS is_month_start,
                (d = (date_trunc('month', d) + INTERVAL 1 MONTH - INTERVAL 1 DAY)::DATE) AS is_month_end
            FROM all_distinct_dates
            ORDER BY d;
        """)

        # dim_grade
        con.execute("""
            INSERT INTO dim_grade
            SELECT
                grade_number AS grade_key,
                grade_number,
                'Grade ' || CAST(grade_number AS VARCHAR) AS grade_label
            FROM (SELECT DISTINCT grade_number FROM p_attendance WHERE grade_number IS NOT NULL)
            ORDER BY grade_number;
        """)

        # dim_subject
        con.execute("""
            INSERT INTO dim_subject
            SELECT
                ROW_NUMBER() OVER(ORDER BY subject_standard) AS subject_key,
                subject_standard,
                CASE
                    WHEN subject_standard IN ('Mathematics', 'Science') THEN 'STEM'
                    WHEN subject_standard IN ('English', 'Hindi', 'Punjabi') THEN 'Language'
                    ELSE 'Social & General'
                END AS subject_category
            FROM (SELECT DISTINCT subject_standard FROM p_assessments WHERE subject_standard IS NOT NULL)
            ORDER BY subject_standard;
        """)

        # dim_vendor
        con.execute("""
            INSERT INTO dim_vendor
            SELECT
                ROW_NUMBER() OVER(ORDER BY vendor_id) AS vendor_key,
                vendor_id,
                vendor_name,
                vendor_name AS vendor_name_standard
            FROM (SELECT DISTINCT vendor_id, vendor_name FROM p_procurement WHERE vendor_id IS NOT NULL)
            ORDER BY vendor_id;
        """)

        # dim_grain
        con.execute("""
            INSERT INTO dim_grain
            SELECT
                ROW_NUMBER() OVER(ORDER BY grain_standard) AS grain_key,
                grain_standard,
                price_per_kg,
                'Official Analytical Price Schedule' AS price_source,
                'Kilogram' AS unit_basis
            FROM (SELECT DISTINCT grain_standard, price_per_kg FROM p_procurement WHERE grain_standard IS NOT NULL)
            ORDER BY grain_standard;
        """)

        # -------------------------------------------------------------
        # 4. POPULATE FACTS
        # -------------------------------------------------------------
        logger.info("Populating fact tables...")

        # fact_attendance
        con.execute("""
            INSERT INTO fact_attendance
            SELECT
                ROW_NUMBER() OVER() AS record_key,
                a.record_id,
                s.school_key,
                d.date_key,
                g.grade_key,
                a.school_id,
                CAST(a.date AS DATE) AS date,
                a.grade_number,
                a.total_students,
                a.present_students,
                a.attendance_rate,
                a.teacher_present_clean AS teacher_present,
                a.marked_by,
                a.is_impossible_attendance,
                a.is_proxy_attendance,
                a.is_trusted_attendance,
                a.quality_status,
                a.attendance_anomaly_reason
            FROM p_attendance a
            JOIN dim_school s ON a.school_id = s.school_id
            JOIN dim_date d ON CAST(a.date AS DATE) = d.date
            JOIN dim_grade g ON a.grade_number = g.grade_number;
        """)

        # fact_assessment
        con.execute("""
            INSERT INTO fact_assessment
            SELECT
                ROW_NUMBER() OVER() AS assessment_key,
                t.assessment_id,
                s.school_key,
                d.date_key,
                g.grade_key,
                sub.subject_key,
                t.school_id,
                CAST(t.date AS DATE) AS date,
                t.grade AS grade_number,
                t.subject_standard,
                t.grading_scale_raw AS grading_scale,
                t.normalized_score_pct,
                t.score_normalization_method,
                t.is_letter_grade_proxy,
                t.total_students_assessed,
                t.quality_status
            FROM p_assessments t
            JOIN dim_school s ON t.school_id = s.school_id
            JOIN dim_date d ON CAST(t.date AS DATE) = d.date
            JOIN dim_grade g ON t.grade = g.grade_number
            JOIN dim_subject sub ON t.subject_standard = sub.subject_standard;
        """)

        # fact_infrastructure
        con.execute("""
            INSERT INTO fact_infrastructure
            SELECT
                ROW_NUMBER() OVER() AS inspection_key,
                i.inspection_id,
                s.school_key,
                d.date_key,
                i.school_id,
                CAST(i.date AS DATE) AS date,
                i.has_electricity,
                i.has_drinking_water,
                i.has_functional_toilet,
                i.has_boundary_wall,
                i.has_playground,
                i.inspector_name,
                i.remarks
            FROM p_infrastructure i
            JOIN dim_school s ON i.school_id = s.school_id
            JOIN dim_date d ON CAST(i.date AS DATE) = d.date;
        """)

        # fact_procurement
        con.execute("""
            INSERT INTO fact_procurement
            SELECT
                ROW_NUMBER() OVER() AS procurement_key,
                p.procurement_id,
                s.school_key,
                d.date_key,
                v.vendor_key,
                gr.grain_key,
                p.school_id,
                CAST(p.date AS DATE) AS date,
                p.vendor_id,
                p.grain_standard,
                p.quantity_kg,
                p.unit_standard,
                p.price_per_kg,
                p.total_cost,
                p.payment_status,
                p.quantity_rescue_method,
                p.cost_rescue_method,
                p.quality_status
            FROM p_procurement p
            JOIN dim_school s ON p.school_id = s.school_id
            JOIN dim_date d ON CAST(p.date AS DATE) = d.date
            JOIN dim_vendor v ON p.vendor_id = v.vendor_id
            JOIN dim_grain gr ON p.grain_standard = gr.grain_standard;
        """)

        # -------------------------------------------------------------
        # 5. EXECUTE ANALYTICAL SQL VIEWS
        # -------------------------------------------------------------
        logger.info("Executing analytical views...")
        execute_sql_file(con, VIEWS_SQL_PATH)

        # -------------------------------------------------------------
        # 6. MODEL INTEGRITY & ROW COUNT AUDIT
        # -------------------------------------------------------------
        tables = [
            "dim_school",
            "dim_date",
            "dim_grade",
            "dim_subject",
            "dim_vendor",
            "dim_grain",
            "fact_attendance",
            "fact_assessment",
            "fact_infrastructure",
            "fact_procurement",
        ]

        views = [
            "school_performance",
            "school_welfare",
            "district_performance",
            "procurement_summary",
            "school_data_quality",
            "school_risk",
            "school_intervention_priority",
            "school_welfare_gap",
            "district_risk_summary",
            "procurement_anomalies",
        ]

        table_counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tables}
        view_counts = {v: con.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0] for v in views}

        # Golden Integrity Checks
        unmatched_att = con.execute(
            "SELECT COUNT(*) FROM fact_attendance f LEFT JOIN dim_school s ON f.school_key = s.school_key WHERE s.school_key IS NULL"
        ).fetchone()[0]
        unmatched_ass = con.execute(
            "SELECT COUNT(*) FROM fact_assessment f LEFT JOIN dim_school s ON f.school_key = s.school_key WHERE s.school_key IS NULL"
        ).fetchone()[0]
        unmatched_inf = con.execute(
            "SELECT COUNT(*) FROM fact_infrastructure f LEFT JOIN dim_school s ON f.school_key = s.school_key WHERE s.school_key IS NULL"
        ).fetchone()[0]
        unmatched_pro = con.execute(
            "SELECT COUNT(*) FROM fact_procurement f LEFT JOIN dim_school s ON f.school_key = s.school_key WHERE s.school_key IS NULL"
        ).fetchone()[0]

        integrity_passed = (
            unmatched_att == 0 and unmatched_ass == 0 and unmatched_inf == 0 and unmatched_pro == 0
        )

        elapsed = round(time.time() - start_time, 2)
        logger.info(
            "Database build completed in %ss. Integrity Passed: %s", elapsed, integrity_passed
        )

        report = {
            "build_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "elapsed_seconds": elapsed,
            "database_path": str(target_db),
            "table_counts": table_counts,
            "view_counts": view_counts,
            "foreign_key_orphans": {
                "fact_attendance": unmatched_att,
                "fact_assessment": unmatched_ass,
                "fact_infrastructure": unmatched_inf,
                "fact_procurement": unmatched_pro,
            },
            "integrity_passed": integrity_passed,
        }

        # Export validation report
        val_report_path = PROCESSED_DATA_DIR / "model_validation_report.json"
        with open(val_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report

    finally:
        con.close()


if __name__ == "__main__":
    report = build_canonical_database()
    print("Database built successfully.")
    print("Tables:", report["table_counts"])
    print("Views:", report["view_counts"])
    print("Integrity Passed:", report["integrity_passed"])
