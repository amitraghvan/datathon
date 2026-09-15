"""Schemas for Welfare & Infrastructure Intelligence."""

from typing import Dict, List, Optional

from pydantic import BaseModel


class AmenityDistributionItem(BaseModel):
    """Distribution metrics for a single infrastructure amenity."""

    amenity_name: str
    available_count: int
    missing_count: int
    unknown_count: int
    availability_rate_pct: float
    reporting_coverage_pct: float


class ElectricityComparisonItem(BaseModel):
    """Comparative performance based on functional electricity availability."""

    electricity: Optional[str] = None
    electricity_label: str
    school_count: int
    avg_academic_score: float
    avg_attendance_rate: float
    avg_data_coverage_score: float


class WelfareMatrixPoint(BaseModel):
    """Point in the 2x2 Welfare Gap Matrix."""

    school_id: str
    school_name: str
    district: str
    infrastructure_readiness_pct: float
    academic_score: float
    welfare_quadrant: str
    intervention_priority_score: float


class WelfareOverviewResponse(BaseModel):
    """Aggregated welfare and infrastructure response."""

    total_schools: int
    avg_infrastructure_readiness: float
    amenity_distributions: List[AmenityDistributionItem]
    electricity_comparison: List[ElectricityComparisonItem]
    welfare_gap_matrix: List[WelfareMatrixPoint]
    quadrant_counts: Dict[str, int]
    non_causal_disclaimer: str = (
        "Observed performance differences across infrastructure tiers describe historical "
        "associations and must not be interpreted as direct causal evidence."
    )
