"""Common data structures, contextual metric envelopes, and filter models."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """System health and warehouse status."""

    status: str = "healthy"
    version: str = "1.0.0"
    warehouse_connected: bool = True
    trust_score: float = 94.6


class MetricContext(BaseModel):
    """Consulting-grade contextual envelope for all analytical numbers."""

    value: float
    unit: str
    metric: str
    coverage_pct: float
    source: str
    method: str
    benchmark: Optional[float] = None


class ChartEnvelope(BaseModel):
    """Standardized chart data response."""

    metric: str
    title: str
    unit: str
    dimensions: List[str]
    series: List[str] = Field(default_factory=list)
    data: List[Dict[str, Any]]
    coverage: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


class FilterParams(BaseModel):
    """Standard cascading filter parameters supported across endpoints."""

    district: Optional[str] = None
    block: Optional[str] = None
    school_id: Optional[str] = None
    school_type: Optional[str] = None
    medium: Optional[str] = None
    grade: Optional[str] = None
    subject: Optional[str] = None
    risk_tier: Optional[str] = None
    primary_driver: Optional[str] = None
    welfare_quadrant: Optional[str] = None


class DimensionOptionsResponse(BaseModel):
    """Available distinct options for cascading dropdowns."""

    districts: List[str]
    blocks_by_district: Dict[str, List[str]]
    school_types: List[str]
    mediums: List[str]
    risk_tiers: List[str]
    drivers: List[str]
    welfare_quadrants: List[str]
