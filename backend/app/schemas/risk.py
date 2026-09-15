"""Schemas for Risk & Intervention Prioritization."""

from typing import Any, Dict, List

from pydantic import BaseModel


class DriverDistributionItem(BaseModel):
    """Distribution of primary analytical drivers."""

    driver: str
    school_count: int
    percentage: float


class PrioritySchoolItem(BaseModel):
    """School entry in the administrative triaging queue."""

    rank: int
    school_id: str
    school_name: str
    district: str
    block: str
    enrollment: int
    intervention_priority_score: float
    intervention_priority_tier: str
    risk_score: float
    risk_tier: str
    primary_driver: str
    secondary_driver: str
    attendance_rate_pct: float
    academic_score: float
    infrastructure_readiness_pct: float
    recommended_action: str


class RiskSummaryResponse(BaseModel):
    """Executive operational triaging overview."""

    total_schools: int
    priority_school_count: int  # Priority >= 35.0
    high_priority_count: int     # Priority >= 45.0
    critical_risk_count: int     # Risk >= 70.0 (strictly 0 in observed cohort)
    critical_welfare_quadrant_count: int  # Infra < 50 AND Acad < 65

    driver_distribution: List[DriverDistributionItem]
    risk_tier_distribution: Dict[str, int]
    priority_tier_distribution: Dict[str, int]
    risk_vs_priority_points: List[Dict[str, Any]]
    policy_action_catalog: List[Dict[str, str]]
    sensitivity_proof: Dict[str, Any]
