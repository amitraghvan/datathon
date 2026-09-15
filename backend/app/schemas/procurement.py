"""Schemas for Mid-Day Meal Procurement Intelligence."""

from typing import Any, Dict, List

from pydantic import BaseModel


class ProcurementAnomalyItem(BaseModel):
    """Peer Benchmark Exception record (1.5 IQR threshold)."""

    school_id: str
    school_name: str
    district: str
    enrollment: int
    total_spend_inr: float
    total_quantity_kg: float
    avg_cost_per_student: float
    spend_per_student_iqr_threshold: float
    procurement_anomaly_reason: str
    operational_context: str


class ProcurementOverviewResponse(BaseModel):
    """Aggregate procurement metrics and peer benchmark distributions."""

    total_spend_inr: float
    total_quantity_kg: float
    avg_cost_per_kg: float
    avg_cost_per_student: float
    schools_covered: int
    outlier_count: int

    spend_by_district: List[Dict[str, Any]]
    quantity_by_grain: List[Dict[str, Any]]
    vendor_breakdown: List[Dict[str, Any]]
    anomalies: List[ProcurementAnomalyItem]
    governance_notice: str = (
        "This identifies observations that differ materially from comparable peer patterns (75th percentile + 1.5 IQR); "
        "it is not evidence of fraud."
    )
