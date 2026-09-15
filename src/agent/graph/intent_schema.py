"""Structured AgentIntent schema validated using Pydantic v2."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """Canonical classification of user query analytical intents."""

    LOOKUP = "lookup"
    RANKING = "ranking"
    COMPARISON = "comparison"
    TREND = "trend"
    BREAKDOWN = "breakdown"
    DIAGNOSIS = "diagnosis"
    ASSOCIATION = "association"
    SEGMENTATION = "segmentation"
    ANOMALY = "anomaly"
    RECOMMENDATION = "recommendation"
    METHODOLOGY = "methodology"
    DATA_QUALITY = "data_quality"

    # Business domain intent aliases
    DISTRICT_BENCHMARK = "district_benchmark"
    INTERVENTION_PRIORITY_RANKING = "intervention_priority_ranking"
    ATTENDANCE_LEARNING_CORRELATION = "attendance_learning_correlation"
    MDM_ANOMALY_AUDIT = "mdm_anomaly_audit"
    INFRASTRUCTURE_IMPACT = "infrastructure_impact"
    SCHOOL_DEEP_DIVE = "school_deep_dive"
    DATA_QUALITY_DIAGNOSTIC = "data_quality_diagnostic"
    RETENTION_RISK_OVERVIEW = "retention_risk_overview"
    GENERAL_QUESTION = "general_question"


class AgentIntent(BaseModel):
    """Validated intermediate representation of administrator question intent."""

    intent_type: IntentType
    entity: str = "school"
    metric: str = "intervention_priority"
    dimensions: List[str] = Field(default_factory=list)
    filters: Dict[str, Any] = Field(default_factory=dict)
    time_range: Optional[str] = None
    limit: int = 10
    comparison: Optional[Dict[str, Any]] = None
    requested_chart: Optional[str] = None
    needs_explanation: bool = False
    raw_query: str = ""
    confidence: float = 1.0

    @property
    def entities(self) -> Dict[str, Any]:
        """Convenience dictionary combining entity filters and targets."""
        res = dict(self.filters)
        if self.entity:
            res["target_entity"] = self.entity
        return res


def classify_intent_heuristic(query: str) -> IntentType:
    """Deterministic rule-based intent classifier as zero-latency baseline and fallback."""
    q = query.lower()

    # 1. Methodology & Data Quality
    if "how trustworthy" in q or "data quality" in q or "gate" in q or "reliable" in q or "coverage" in q or "excluded" in q or "quarantine" in q or "data trust" in q or "completeness" in q:
        return IntentType.DATA_QUALITY
    if "methodology" in q or "how is" in q and ("calculated" in q or "computed" in q or "defined" in q):
        return IntentType.METHODOLOGY

    # 2. Diagnosis & Explanation
    if q.startswith("why ") or "why is" in q or "reason for" in q or "driver behind" in q or "explain" in q:
        return IntentType.DIAGNOSIS

    # 3. Policy Recommendation
    if "recommend" in q or "what should" in q or "focus on" in q or "action" in q or "strategy" in q:
        return IntentType.RECOMMENDATION

    # 4. Statistical Association
    if "relat" in q or "correlat" in q or "associat" in q or "depend on" in q or "impact" in q:
        return IntentType.ASSOCIATION

    # 5. Outliers & Anomalies
    if "outlier" in q or "exception" in q or "anomaly" in q or "unusual" in q:
        return IntentType.ANOMALY

    # 6. Segmentation / Clustering
    if "cluster" in q or "segment" in q or "quadrant" in q or "welfare gap" in q or "resilient" in q:
        return IntentType.SEGMENTATION

    # 7. Comparison
    if "compare" in q or " vs " in q or "versus" in q or "difference between" in q:
        return IntentType.COMPARISON

    # 8. Trends
    if "trend" in q or "over time" in q or "daily" in q or "timeseries" in q or "temporal" in q:
        return IntentType.TREND

    # 9. Breakdown
    if "breakdown" in q or "distribution" in q or "by district" in q and not ("top" in q or "rank" in q):
        return IntentType.BREAKDOWN

    # 10. Ranking
    if "top" in q or "highest" in q or "lowest" in q or "rank" in q or "worst" in q or "best" in q or "first" in q:
        return IntentType.RANKING

    # 11. Single Entity Lookup
    if re_match_school(q):
        return IntentType.LOOKUP

    return IntentType.RANKING


def re_match_school(q: str) -> bool:
    import re
    return bool(re.search(r"\bSCH[\s_-]?\d+\b", q, re.IGNORECASE))
