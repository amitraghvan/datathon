"""Service for School Welfare & Physical Infrastructure Analytics."""

from typing import Any, Dict, List

from backend.app.repository.duckdb import DuckDBRepository
from backend.app.repository.filters import build_where_clause
from backend.app.repository.queries import (
    ELECTRICITY_IMPACT_ANALYSIS_SQL,
    SCHOOL_MASTER_ENRICHED_SQL,
)
from backend.app.schemas.welfare import (
    AmenityDistributionItem,
    ElectricityComparisonItem,
    WelfareMatrixPoint,
    WelfareOverviewResponse,
)


class WelfareService:
    """Computes infrastructure readiness, amenity coverage, and welfare matrix."""

    def __init__(self, repo: DuckDBRepository) -> None:
        self.repo = repo

    def get_welfare_overview(self, filters: Dict[str, Any]) -> WelfareOverviewResponse:
        """Fetch comprehensive welfare metrics for active filter scope."""
        where_clause, params = build_where_clause(filters, table_alias="base")
        sql = f"WITH base AS ({SCHOOL_MASTER_ENRICHED_SQL}) SELECT * FROM base WHERE {where_clause}"
        df = self.repo.query_df(sql, params)

        if df.empty:
            return WelfareOverviewResponse(
                total_schools=0,
                avg_infrastructure_readiness=0.0,
                amenity_distributions=[],
                electricity_comparison=[],
                welfare_gap_matrix=[],
                quadrant_counts={},
            )

        total_schools = len(df)
        avg_infra = float(df["infrastructure_readiness_pct"].mean())

        # 1. Amenity Distributions (Strictly respecting TRUE, FALSE, UNKNOWN)
        amenity_cols = [
            ("Electricity", "electricity"),
            ("Drinking Water", "drinking_water"),
            ("Functional Toilet", "functional_toilet"),
            ("Boundary Wall", "boundary_wall"),
            ("Playground", "playground"),
        ]

        amenity_dists: List[AmenityDistributionItem] = []
        for label, col in amenity_cols:
            avail = int((df[col] == True).sum())  # noqa: E712
            missing = int((df[col] == False).sum())  # noqa: E712
            unknown = int(df[col].isna().sum())
            reported = avail + missing
            rate = round((avail / reported * 100.0), 1) if reported > 0 else 0.0
            cov = round((reported / total_schools * 100.0), 1) if total_schools > 0 else 0.0

            amenity_dists.append(
                AmenityDistributionItem(
                    amenity_name=label,
                    available_count=avail,
                    missing_count=missing,
                    unknown_count=unknown,
                    availability_rate_pct=rate,
                    reporting_coverage_pct=cov,
                )
            )

        # 2. Electricity Impact Comparison (Competition Requirement)
        elec_records = self.repo.query_dicts(ELECTRICITY_IMPACT_ANALYSIS_SQL)
        elec_items: List[ElectricityComparisonItem] = []
        for r in elec_records:
            raw_val = r["electricity"]
            val_str = str(raw_val).upper() if raw_val is not None else "UNKNOWN"
            if val_str in ("TRUE", "1"):
                label = "With Functional Electricity"
                norm_val = "TRUE"
            elif val_str in ("FALSE", "0"):
                label = "Without Functional Electricity"
                norm_val = "FALSE"
            else:
                label = "Electricity Status Unknown"
                norm_val = "UNKNOWN"

            elec_items.append(
                ElectricityComparisonItem(
                    electricity=norm_val,
                    electricity_label=label,
                    school_count=int(r["school_count"]),
                    avg_academic_score=float(r["avg_academic_score"]),
                    avg_attendance_rate=float(r["avg_attendance_rate"]),
                    avg_data_coverage_score=float(r["avg_data_coverage_score"]),
                )
            )

        # 3. Welfare Gap Matrix Points
        matrix_points = [
            WelfareMatrixPoint(
                school_id=r["school_id"],
                school_name=r["school_name"],
                district=r["district"],
                infrastructure_readiness_pct=float(r["infrastructure_readiness_pct"]),
                academic_score=float(r["academic_score"]),
                welfare_quadrant=r["welfare_quadrant"],
                intervention_priority_score=float(r["intervention_priority_score"]),
            )
            for _, r in df.iterrows()
        ]

        # 4. Quadrant counts
        quad_counts = df["welfare_quadrant"].value_counts().to_dict()

        return WelfareOverviewResponse(
            total_schools=total_schools,
            avg_infrastructure_readiness=round(avg_infra, 1),
            amenity_distributions=amenity_dists,
            electricity_comparison=elec_items,
            welfare_gap_matrix=matrix_points,
            quadrant_counts=quad_counts,
        )
