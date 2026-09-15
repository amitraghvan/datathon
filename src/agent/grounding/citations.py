"""Verifiable Evidence Citation engine linking claims to specific warehouse views and records."""

import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EvidenceCitation(BaseModel):
    """Verifiable pointer to a canonical warehouse record and metric."""

    source_view: str
    record_identifier: str
    metric_id: str
    metric_name: str
    value: Any
    unit: str
    driver: Optional[str] = None
    district: Optional[str] = None
    generated_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    methodology_reference: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert citation to dictionary."""
        return self.model_dump()


def generate_citations(first_arg: Any, second_arg: Any) -> List[EvidenceCitation]:
    """Extract verifiable evidence citations from executed DuckDB result rows."""
    # Determine which argument is records vs metric/plan
    if hasattr(first_arg, "metric"):
        # first_arg is QueryPlan
        metric_contract = first_arg.metric
        records = second_arg.records if hasattr(second_arg, "records") else second_arg
    elif hasattr(second_arg, "metric"):
        # second_arg is QueryPlan
        metric_contract = second_arg.metric
        records = first_arg.records if hasattr(first_arg, "records") else first_arg
    elif hasattr(second_arg, "source_columns"):
        metric_contract = second_arg
        records = first_arg.records if hasattr(first_arg, "records") else first_arg
    else:
        metric_contract = getattr(first_arg, "metric", None)
        records = second_arg if isinstance(second_arg, list) else []

    if not records or not metric_contract:
        return []

    citations: List[EvidenceCitation] = []

    for r in records[:10]:  # Cap citations to top 10 items
        record_id = r.get("school_id") or r.get("district") or r.get("block") or r.get("commodity") or "RECORD"

        val = None
        source_cols = getattr(metric_contract, "source_columns", [])
        for col in source_cols:
            if col in r and r[col] is not None:
                val = r[col]
                break
        if val is None:
            val = (
                r.get("avg_attendance_rate")
                or r.get("attendance_rate_pct")
                or r.get("intervention_priority_score")
                or r.get("academic_score")
                or r.get("total_spend_inr")
            )

        citations.append(
            EvidenceCitation(
                source_view=getattr(metric_contract, "source_view", "warehouse"),
                record_identifier=str(record_id),
                metric_id=getattr(metric_contract, "metric_id", "metric"),
                metric_name=getattr(metric_contract, "name", "Metric"),
                value=val,
                unit=getattr(metric_contract, "unit", "%"),
                driver=r.get("primary_driver") or r.get("primary_risk_driver"),
                district=r.get("district"),
                methodology_reference=f"Governed view '{getattr(metric_contract, 'source_view', 'warehouse')}', calculated by {getattr(metric_contract, 'calculation_owner', 'Data Governance')}.",
            )
        )

    return citations
