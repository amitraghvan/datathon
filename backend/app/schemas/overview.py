"""Schemas for Executive Command Center."""

from typing import Any, Dict, List

from pydantic import BaseModel

from backend.app.schemas.common import MetricContext


class ExecutiveKPIs(BaseModel):
    """The six core operational KPIs."""

    schools_monitored: MetricContext
    average_attendance: MetricContext
    average_academic_score: MetricContext
    priority_schools: MetricContext
    infrastructure_readiness: MetricContext
    data_quality_coverage: MetricContext


class DynamicAlert(BaseModel):
    """Dynamically generated executive alert item."""

    title: str
    finding: str
    evidence: str
    interpretation: str
    limitation: str
    level: str = "info"  # "critical", "warning", "info", "success"


class ExecutiveOverviewResponse(BaseModel):
    """Complete payload for Executive Command Center."""

    kpis: ExecutiveKPIs
    alerts: List[DynamicAlert]
    district_ranking: List[Dict[str, Any]]
    welfare_matrix: List[Dict[str, Any]]
    attendance_academic_summary: Dict[str, Any]
    top_priorities: List[Dict[str, Any]]
    trust_pipeline: Dict[str, Any]
    active_filters: Dict[str, Any]
