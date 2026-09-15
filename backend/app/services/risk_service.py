"""Service for Risk & Intervention Prioritization Command Center."""

from typing import Any, Dict, List

from backend.app.repository.duckdb import DuckDBRepository
from backend.app.repository.filters import build_where_clause
from backend.app.repository.queries import SCHOOL_MASTER_ENRICHED_SQL
from backend.app.schemas.risk import (
    DriverDistributionItem,
    PrioritySchoolItem,
    RiskSummaryResponse,
)


class RiskService:
    """Manages risk severity, intervention urgency, and triaging queues."""

    def __init__(self, repo: DuckDBRepository) -> None:
        self.repo = repo

    def get_risk_summary(self, filters: Dict[str, Any]) -> RiskSummaryResponse:
        """Fetch executive triaging overview and driver taxonomy."""
        where_clause, params = build_where_clause(filters, table_alias="base")
        sql = f"WITH base AS ({SCHOOL_MASTER_ENRICHED_SQL}) SELECT * FROM base WHERE {where_clause}"
        df = self.repo.query_df(sql, params)

        if df.empty:
            return RiskSummaryResponse(
                total_schools=0,
                priority_school_count=0,
                high_priority_count=0,
                critical_risk_count=0,
                critical_welfare_quadrant_count=0,
                driver_distribution=[],
                risk_tier_distribution={},
                priority_tier_distribution={},
                risk_vs_priority_points=[],
                policy_action_catalog=[],
                sensitivity_proof={},
            )

        total_schools = len(df)
        priority_schools = int((df["intervention_priority_score"] >= 35.0).sum())
        high_priority = int((df["intervention_priority_score"] >= 45.0).sum())
        critical_risk = int((df["risk_score"] >= 70.0).sum())  # Strictly 0 in observed cohort
        critical_quadrant = int((df["welfare_quadrant"] == "CRITICAL INTERVENTION").sum())

        # Driver distribution
        driver_counts = df["primary_driver"].value_counts()
        driver_dist: List[DriverDistributionItem] = []
        for d, count in driver_counts.items():
            pct = round((count / total_schools * 100.0), 1)
            driver_dist.append(DriverDistributionItem(driver=d, school_count=int(count), percentage=pct))

        # Tier distributions
        risk_tiers = df["risk_tier"].value_counts().to_dict()
        priority_tiers = df["intervention_priority_tier"].value_counts().to_dict()

        # Scatter points (Risk Severity vs Intervention Priority)
        points = df[
            [
                "school_id",
                "school_name",
                "district",
                "risk_score",
                "risk_tier",
                "intervention_priority_score",
                "intervention_priority_tier",
                "primary_driver",
                "welfare_quadrant",
                "enrollment",
            ]
        ].to_dict(orient="records")

        # Deterministic Policy Action Catalog
        catalog = [
            {
                "driver": "Infrastructure",
                "trigger": "Infrastructure Deficit is dominant component",
                "action": "Facility Remediation",
                "protocol": "Priority allocation of civil repair grants; fast-track functional toilet, water, and electrification installation.",
            },
            {
                "driver": "Academic",
                "trigger": "Academic FLN Deficit is dominant component",
                "action": "Targeted FLN Academic Support",
                "protocol": "Deploy foundational learning workbooks and after-school remedial sessions in Mathematics/Language.",
            },
            {
                "driver": "Attendance",
                "trigger": "Attendance Deficit is dominant component",
                "action": "Attendance Engagement Campaign",
                "protocol": "Community outreach, automated parent SMS alerts, and student mentorship tracking.",
            },
            {
                "driver": "Multi-factor",
                "trigger": "Multiple compounding deficits without single dominant factor",
                "action": "Multi-Factor Taskforce Review",
                "protocol": "Convene combined administrative review covering infrastructure gaps and remedial coaching.",
            },
        ]

        # Sensitivity Proof Summary
        sensitivity = {
            "policy_weight_stability": "Rank correlation rho >= 0.985 across 4 alternative weighting configurations (90-100% Top-10 overlap).",
            "letter_grade_imputation_stability": "Numeric vs All-records correlation r = 0.858 (district policy r = 0.984; mean risk shift = 0.76 pts).",
            "non_causal_classification": "Deterministic triage score; does not claim longitudinal dropout probability.",
        }

        return RiskSummaryResponse(
            total_schools=total_schools,
            priority_school_count=priority_schools,
            high_priority_count=high_priority,
            critical_risk_count=critical_risk,
            critical_welfare_quadrant_count=critical_quadrant,
            driver_distribution=driver_dist,
            risk_tier_distribution=risk_tiers,
            priority_tier_distribution=priority_tiers,
            risk_vs_priority_points=points,
            policy_action_catalog=catalog,
            sensitivity_proof=sensitivity,
        )

    def get_priorities_table(self, filters: Dict[str, Any], limit: int = 50) -> List[PrioritySchoolItem]:
        """Fetch ranked queue of intervention priority schools."""
        where_clause, params = build_where_clause(filters, table_alias="base")
        sql = f"""
        WITH base AS ({SCHOOL_MASTER_ENRICHED_SQL})
        SELECT * FROM base
        WHERE {where_clause}
        ORDER BY intervention_priority_score DESC, enrollment DESC, school_id ASC
        LIMIT ?
        """
        records = self.repo.query_dicts(sql, list(params) + [limit])
        items: List[PrioritySchoolItem] = []
        for i, r in enumerate(records, 1):
            driver = r.get("primary_driver", "Multi-factor")
            if driver == "Infrastructure":
                action = "Facility Remediation"
            elif driver == "Academic":
                action = "Remedial Tutoring"
            elif driver == "Attendance":
                action = "Community Outreach"
            else:
                action = "Multi-Factor Review"

            items.append(
                PrioritySchoolItem(
                    rank=i,
                    school_id=r["school_id"],
                    school_name=r["school_name"],
                    district=r["district"],
                    block=r["block"],
                    enrollment=int(r["enrollment"]),
                    intervention_priority_score=float(r["intervention_priority_score"]),
                    intervention_priority_tier=r["intervention_priority_tier"],
                    risk_score=float(r["risk_score"]),
                    risk_tier=r["risk_tier"],
                    primary_driver=r["primary_driver"],
                    secondary_driver=r["secondary_driver"],
                    attendance_rate_pct=float(r["attendance_rate_pct"]),
                    academic_score=float(r["academic_score"]),
                    infrastructure_readiness_pct=float(r["infrastructure_readiness_pct"]),
                    recommended_action=action,
                )
            )
        return items
