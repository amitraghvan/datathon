"""Service for Mid-Day Meal Procurement Intelligence."""

from typing import Any, Dict, List

import pandas as pd

from backend.app.repository.duckdb import DuckDBRepository
from backend.app.repository.filters import build_where_clause
from backend.app.repository.queries import PROCUREMENT_ENRICHED_SQL
from backend.app.schemas.procurement import (
    ProcurementAnomalyItem,
    ProcurementOverviewResponse,
)


class ProcurementService:
    """Computes MDM procurement analytics, unit costs, and IQR anomalies."""

    def __init__(self, repo: DuckDBRepository) -> None:
        self.repo = repo

    def get_procurement_overview(self, filters: Dict[str, Any]) -> ProcurementOverviewResponse:
        """Fetch procurement aggregates and peer benchmark exceptions."""
        where_clause, params = build_where_clause(filters, table_alias="base")
        sql = f"WITH base AS ({PROCUREMENT_ENRICHED_SQL}) SELECT * FROM base WHERE {where_clause}"
        df = self.repo.query_df(sql, params)

        if df.empty:
            return ProcurementOverviewResponse(
                total_spend_inr=0.0,
                total_quantity_kg=0.0,
                avg_cost_per_kg=0.0,
                avg_cost_per_student=0.0,
                schools_covered=0,
                outlier_count=0,
                spend_by_district=[],
                quantity_by_grain=[],
                vendor_breakdown=[],
                anomalies=[],
            )

        total_spend = float(df["total_spend_inr"].sum())
        total_qty = float(df["total_quantity_kg"].sum())
        avg_cost_kg = float(total_spend / total_qty) if total_qty > 0 else 0.0
        avg_cost_stud = float(df["avg_cost_per_student"].mean())
        schools_count = len(df)

        # Spend by district
        spend_dist = (
            df.groupby("district")["total_spend_inr"]
            .sum()
            .reset_index()
            .sort_values(by="total_spend_inr", ascending=False)
            .to_dict(orient="records")
        )

        # Grains and vendor breakdown from fact_procurement
        grain_sql = """
        SELECT g.grain_standard AS grain_name, SUM(p.quantity_kg) as quantity_kg, SUM(p.total_cost) as total_spend_inr
        FROM fact_procurement p
        JOIN dim_grain g ON p.grain_key = g.grain_key
        GROUP BY g.grain_standard
        ORDER BY quantity_kg DESC
        """
        grain_data = self.repo.query_dicts(grain_sql)

        vendor_sql = """
        SELECT v.vendor_name, COUNT(*) as delivery_count, SUM(p.total_cost) as total_spend_inr
        FROM fact_procurement p
        JOIN dim_vendor v ON p.vendor_key = v.vendor_key
        GROUP BY v.vendor_name
        ORDER BY total_spend_inr DESC
        """
        vendor_data = self.repo.query_dicts(vendor_sql)

        # Anomalies (Peer Benchmark Exceptions)
        df_anom = df[df["is_procurement_outlier"] == True].sort_values(by="avg_cost_per_student", ascending=False)  # noqa: E712
        anomalies: List[ProcurementAnomalyItem] = []
        for _, r in df_anom.iterrows():
            enrollment = int(r["enrollment"]) if pd.notnull(r["enrollment"]) else 100
            threshold = float(r["spend_per_student_iqr_threshold"]) if pd.notnull(r["spend_per_student_iqr_threshold"]) else 350.0
            spend_stud = float(r["avg_cost_per_student"])

            # Operational context
            if enrollment < 150:
                context = f"Small scale enrollment ({enrollment} pupils); minimum vendor delivery batch constraint."
            else:
                context = "Higher proportion of cooking oil/pulses or accelerated procurement cadence."

            anomalies.append(
                ProcurementAnomalyItem(
                    school_id=r["school_id"],
                    school_name=r["school_name"],
                    district=r["district"],
                    enrollment=enrollment,
                    total_spend_inr=float(r["total_spend_inr"]),
                    total_quantity_kg=float(r["total_quantity_kg"]),
                    avg_cost_per_student=round(spend_stud, 1),
                    spend_per_student_iqr_threshold=round(threshold, 1),
                    procurement_anomaly_reason=r.get("procurement_anomaly_reason") or "Spend per student exceeds 75th percentile + 1.5 IQR",
                    operational_context=context,
                )
            )

        return ProcurementOverviewResponse(
            total_spend_inr=round(total_spend, 2),
            total_quantity_kg=round(total_qty, 1),
            avg_cost_per_kg=round(avg_cost_kg, 2),
            avg_cost_per_student=round(avg_cost_stud, 2),
            schools_covered=schools_count,
            outlier_count=len(anomalies),
            spend_by_district=spend_dist,
            quantity_by_grain=grain_data,
            vendor_breakdown=vendor_data,
            anomalies=anomalies,
        )
