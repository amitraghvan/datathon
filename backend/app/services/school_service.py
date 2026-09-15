"""Service for School Directory and School 360 decision profile."""

from typing import Any, Dict, List, Optional

from backend.app.repository.duckdb import DuckDBRepository
from backend.app.repository.filters import build_where_clause
from backend.app.repository.queries import (
    DISTRICT_SUMMARY_SQL,
    PROCUREMENT_ENRICHED_SQL,
    SCHOOL_ASSESSMENT_DETAILS_SQL,
    SCHOOL_ATTENDANCE_SERIES_SQL,
    SCHOOL_MASTER_ENRICHED_SQL,
)
from backend.app.schemas.common import DimensionOptionsResponse
from backend.app.schemas.school import (
    AmenityStatusMap,
    AssessmentSubjectItem,
    AttendanceTimeseriesPoint,
    SchoolProcurementSummary,
    SchoolProfileResponse,
    SchoolSummaryItem,
)
from backend.app.utils.errors import SchoolNotFoundException
from backend.app.utils.pagination import PaginatedResponse


class SchoolService:
    """Provides school directory search and School 360 profiling."""

    def __init__(self, repo: DuckDBRepository) -> None:
        self.repo = repo

    def get_schools(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        page_size: int = 25,
        search: Optional[str] = None,
        sort_by: str = "intervention_priority_score",
        sort_desc: bool = True,
    ) -> PaginatedResponse[SchoolSummaryItem]:
        """Fetch paginated, filtered, searchable school directory records."""
        where_clause, params = build_where_clause(filters, table_alias="s")

        if search:
            where_clause += " AND (LOWER(s.school_name) LIKE ? OR LOWER(s.school_id) LIKE ?)"
            s_term = f"%{search.lower().strip()}%"
            params.extend([s_term, s_term])

        order = "DESC" if sort_desc else "ASC"
        # Validate sort column to avoid SQL injection
        allowed_cols = {
            "intervention_priority_score",
            "risk_score",
            "attendance_rate_pct",
            "academic_score",
            "infrastructure_readiness_pct",
            "enrollment",
            "school_name",
        }
        col = sort_by if sort_by in allowed_cols else "intervention_priority_score"

        # Count total
        count_sql = f"WITH s AS ({SCHOOL_MASTER_ENRICHED_SQL}) SELECT COUNT(*) as cnt FROM s WHERE {where_clause}"
        total_rec = self.repo.query_one(count_sql, params)
        total = total_rec["cnt"] if total_rec else 0

        # Fetch page
        offset = (page - 1) * page_size
        data_sql = f"""
        WITH s AS ({SCHOOL_MASTER_ENRICHED_SQL})
        SELECT * FROM s
        WHERE {where_clause}
        ORDER BY {col} {order}, school_id ASC
        LIMIT ? OFFSET ?
        """
        page_params = list(params) + [page_size, offset]
        records = self.repo.query_dicts(data_sql, page_params)
        items = [SchoolSummaryItem(**r) for r in records]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_school_profile(self, school_id: str) -> SchoolProfileResponse:
        """Construct complete School 360 profile."""
        sql = f"WITH s AS ({SCHOOL_MASTER_ENRICHED_SQL}) SELECT * FROM s WHERE school_id = ?"
        record = self.repo.query_one(sql, [school_id])

        if not record:
            raise SchoolNotFoundException(school_id)

        # Amenity map (preserving None as UNKNOWN)
        amenities = AmenityStatusMap(
            electricity=record["electricity"],
            drinking_water=record["drinking_water"],
            functional_toilet=record["functional_toilet"],
            boundary_wall=record["boundary_wall"],
            playground=record["playground"],
        )

        # Deterministic policy action
        driver = record.get("primary_driver", "Multi-factor")
        if driver == "Infrastructure":
            action = "Infrastructure Remediation"
            details = "Prioritize capital funds for missing core amenities (sanitation, drinking water, electricity)."
        elif driver == "Academic":
            action = "Targeted FLN Academic Support"
            details = "Deploy foundational learning workbooks and after-school remedial sessions in Mathematics/Language."
        elif driver == "Attendance":
            action = "Attendance Engagement Campaign"
            details = "Implement parent SMS alerts, community outreach, and transportation assistance."
        else:
            action = "Multi-Factor Taskforce Review"
            details = "Convene combined administrative review covering infrastructure gaps and remedial coaching."

        # Fetch district benchmark
        dist_sql = f"{DISTRICT_SUMMARY_SQL.replace('ORDER BY d.district ASC', '')} WHERE d.district = ?"
        dist_row = self.repo.query_one(dist_sql, [record["district"]]) or {}
        benchmarks = {
            "district_avg_attendance": dist_row.get("avg_attendance_rate", 78.5),
            "district_avg_academic": dist_row.get("avg_academic_score", 65.0),
            "district_avg_infrastructure": dist_row.get("avg_infrastructure_readiness", 70.0),
        }

        return SchoolProfileResponse(
            school_id=record["school_id"],
            school_name=record["school_name"],
            district=record["district"],
            block=record["block"],
            school_type=record["school_type"],
            medium=record["medium"],
            enrollment=record["enrollment"],
            student_teacher_ratio=record["student_teacher_ratio"],
            attendance_rate_pct=record["attendance_rate_pct"],
            academic_score=record["academic_score"],
            infrastructure_readiness_pct=record["infrastructure_readiness_pct"],
            risk_score=record["risk_score"],
            risk_tier=record["risk_tier"],
            intervention_priority_score=record["intervention_priority_score"],
            intervention_priority_tier=record["intervention_priority_tier"],
            welfare_quadrant=record["welfare_quadrant"],
            quadrant_action=record.get("quadrant_action"),
            primary_driver=record["primary_driver"],
            secondary_driver=record["secondary_driver"],
            attendance_deficit=record["attendance_deficit"],
            academic_deficit=record["academic_deficit"],
            infrastructure_deficit=record["infrastructure_deficit"],
            data_coverage_score=record["data_coverage_score"],
            confidence_score=record["confidence_score"],
            amenities=amenities,
            amenities_available_count=record.get("amenities_available_count", 0),
            amenities_reported_count=record.get("amenities_reported_count", 0),
            recommended_action=action,
            recommendation_details=details,
            district_benchmark=benchmarks,
        )

    def get_school_attendance_timeseries(self, school_id: str) -> List[AttendanceTimeseriesPoint]:
        """Fetch daily attendance observations for school."""
        # Verify school exists
        self.get_school_profile(school_id)
        records = self.repo.query_dicts(SCHOOL_ATTENDANCE_SERIES_SQL, [school_id])
        return [
            AttendanceTimeseriesPoint(
                date=str(r["date"]),
                present=int(r["present"]),
                total=int(r["total"]),
                attendance_pct=float(r["attendance_pct"]),
                records_count=int(r["records_count"]),
                has_flagged_record=bool(r["has_flagged_record"]),
                has_proxy_record=bool(r["has_proxy_record"]),
            )
            for r in records
        ]

    def get_school_academics(self, school_id: str) -> List[AssessmentSubjectItem]:
        """Fetch subject and grade level test performance."""
        self.get_school_profile(school_id)
        records = self.repo.query_dicts(SCHOOL_ASSESSMENT_DETAILS_SQL, [school_id])
        return [
            AssessmentSubjectItem(
                subject=r["subject"],
                grade=int(r["grade"]),
                avg_score=float(r["avg_score"]),
                assessment_count=int(r["assessment_count"]),
                avg_total_marks=float(r["avg_total_marks"]),
                has_proxy_score=bool(r["has_proxy_score"]),
            )
            for r in records
        ]

    def get_school_procurement(self, school_id: str) -> Optional[SchoolProcurementSummary]:
        """Fetch procurement summary for a single school."""
        self.get_school_profile(school_id)
        sql = f"SELECT * FROM ({PROCUREMENT_ENRICHED_SQL}) WHERE school_id = ?"
        r = self.repo.query_one(sql, [school_id])
        if not r:
            return None
        return SchoolProcurementSummary(
            school_id=r["school_id"],
            school_name=r["school_name"],
            district=r["district"],
            total_spend_inr=float(r["total_spend_inr"]),
            total_quantity_kg=float(r["total_quantity_kg"]),
            procurement_records=int(r["procurement_records"]),
            avg_cost_per_kg=float(r["avg_cost_per_kg"]),
            avg_cost_per_student=float(r["avg_cost_per_student"]),
            grain_count=int(r["grain_count"]),
            vendor_count=int(r["vendor_count"]),
            is_procurement_outlier=bool(r["is_procurement_outlier"]),
            procurement_anomaly_reason=r.get("procurement_anomaly_reason"),
            spend_per_student_iqr_threshold=r.get("spend_per_student_iqr_threshold"),
        )

    def get_dimension_options(self) -> DimensionOptionsResponse:
        """Fetch unique dimension options and block mappings for cascading filters."""
        df_schools = self.repo.query_df("SELECT DISTINCT district, block, school_type, medium FROM dim_school")
        districts = sorted([d for d in df_schools["district"].dropna().unique().tolist() if d])

        blocks_by_district: Dict[str, List[str]] = {}
        for d in districts:
            sub = df_schools[df_schools["district"] == d]
            blocks = sorted([b for b in sub["block"].dropna().unique().tolist() if b])
            blocks_by_district[d] = blocks

        school_types = sorted([st for st in df_schools["school_type"].dropna().unique().tolist() if st])
        mediums = sorted([m for m in df_schools["medium"].dropna().unique().tolist() if m])

        return DimensionOptionsResponse(
            districts=districts,
            blocks_by_district=blocks_by_district,
            school_types=school_types,
            mediums=mediums,
            risk_tiers=["LOW", "MODERATE", "CRITICAL"],
            drivers=["Infrastructure", "Academic", "Attendance", "Multi-factor"],
            welfare_quadrants=["MODEL", "RESILIENT", "ACADEMIC INTERVENTION", "CRITICAL INTERVENTION"],
        )
