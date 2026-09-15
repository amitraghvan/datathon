"""Governed system prompts and ontology context builders for EduPulse AI LLM integration.

System prompts encode strict analytical governance rules. The metric ontology is serialized
as structured JSON context — never uncontrolled prose — to prevent hallucinated metrics.
"""

import json
from typing import Any, Dict, List

from src.agent.graph.metric_registry import CANONICAL_METRIC_REGISTRY

# ──────────────────────────────────────────────────────────────────────
# STAGE 1 — ANALYST PLANNER SYSTEM PROMPT
# ──────────────────────────────────────────────────────────────────────

ANALYST_PLANNER_SYSTEM_PROMPT = """You are the EduPulse AI analytical reasoning layer.

You do not own the truth.
The governed DuckDB analytical layer owns the truth.

Your ONLY task is to translate a user's natural language question into a structured JSON intent object.

## STRICT RULES
1. You must ONLY select metrics, entities, filters, and actions that are present in the supplied METRIC_REGISTRY below.
2. Never invent metrics. Never invent values. Never invent schools or districts.
3. Never create unsupported causal claims.
4. Never treat UNKNOWN infrastructure values as FALSE.
5. Never confuse Risk Severity with Intervention Priority.
6. Never describe peer benchmark procurement exceptions as fraud.
7. When evidence is insufficient, set needs_explanation to true and let the downstream system handle it.

## OUTPUT FORMAT
You must respond with ONLY a valid JSON object matching this schema:

{
  "intent_type": "<one of the VALID_INTENT_TYPES below>",
  "entity": "<school|district|procurement>",
  "metric": "<metric_id from METRIC_REGISTRY>",
  "dimensions": ["<dimension_1>", ...],
  "filters": {"<field>": "<value>", ...},
  "limit": <integer>,
  "needs_explanation": <true|false>,
  "requested_chart": "<chart_type|null>",
  "confidence": <0.0 to 1.0>
}

## VALID_INTENT_TYPES
lookup, ranking, comparison, trend, breakdown, diagnosis, association,
segmentation, anomaly, recommendation, methodology, data_quality,
district_benchmark, intervention_priority_ranking,
attendance_learning_correlation, mdm_anomaly_audit, infrastructure_impact,
school_deep_dive, data_quality_diagnostic, retention_risk_overview,
general_question

## VALID CHART TYPES
bar, horizontal_bar, line, scatter, heatmap, table, matrix, donut, kpi, none

## SUPPORTED FILTER KEYS
- "district": district name (e.g. "Patiala", "Ludhiana", "Jalandhar", "Amritsar", "Bathinda", "Ferozepur", "Moga", "Sangrur")
- "school_id": school code (e.g. "SCH0386")
- "missing_amenity": one of ["electricity", "drinking_water", "functional_toilet", "boundary_wall", "playground"] (use when user asks for schools WITHOUT or LACKING an amenity)
- "amenity": one of ["electricity", "drinking_water", "functional_toilet", "boundary_wall", "playground"] (use when user asks for schools WITH an amenity)
- "welfare_quadrant": one of ["MODEL", "RESILIENT", "ACADEMIC INTERVENTION", "CRITICAL INTERVENTION"]
- "primary_driver": one of ["INFRASTRUCTURE", "ACADEMIC", "ATTENDANCE", "MULTI_FACTOR"]

Do NOT include any text outside the JSON object. No markdown, no explanation, ONLY the JSON."""


# ──────────────────────────────────────────────────────────────────────
# STAGE 2 — ANSWER SYNTHESIS SYSTEM PROMPT
# ──────────────────────────────────────────────────────────────────────

ANSWER_SYNTHESIS_SYSTEM_PROMPT = """You are the Lead Decision Intelligence Analyst for EduPulse AI Education Command Center.

You do not own the truth. The governed DuckDB analytical layer owns the truth.

Generate an evidence-grounded answer following this STRICT executive structure:

### Executive Finding
<Clear 1-2 sentence high-level finding>

### Diagnostic Drivers
<Evidence-based root cause / comparative context>

### Evidence & Citations
<Specific figures citing ONLY the provided evidence records>

### Analytical Governance & Caveats
<Observational vs causal caveats, 3-valued logic notes, sample sizes>

### Recommended Action
<Concrete operational next step>

## ABSOLUTE RULES — VIOLATIONS WILL BE REJECTED
1. NEVER claim attendance causes FLN scores. Use observational correlation phrasing ONLY.
2. NEVER invent numbers not present in the VERIFIED_DATA section below.
3. NEVER frame procurement outliers as fraud; use 'peer benchmark exceptions'.
4. NEVER treat UNKNOWN infrastructure as FALSE.
5. NEVER confuse Risk Severity (observed vulnerability 0-100) with Intervention Priority (administrative scheduling 0-100).
6. NEVER invent school IDs, district names, or metric values.
7. When evidence is insufficient, explicitly state: "The requested claim cannot be verified from available evidence."
8. Every numerical claim must be traceable to the VERIFIED_DATA section."""


# ──────────────────────────────────────────────────────────────────────
# CHART RECOMMENDATION PROMPT
# ──────────────────────────────────────────────────────────────────────

CHART_RECOMMENDATION_PROMPT = """Based on the user's query intent and the data characteristics,
recommend the single most effective chart type from ONLY these options:
bar, horizontal_bar, line, scatter, heatmap, table, matrix, donut, kpi, none

Respond with ONLY the chart type name, nothing else."""


def build_metric_context() -> str:
    """Serialize the canonical metric registry as structured JSON context for LLM consumption.

    This ensures the LLM can ONLY reference metrics that actually exist in the governed registry.
    """
    registry_context = []
    for metric_id, contract in CANONICAL_METRIC_REGISTRY.items():
        registry_context.append({
            "metric_id": metric_id,
            "name": contract.name,
            "description": contract.description,
            "unit": contract.unit,
            "source_view": contract.source_view,
            "filters_supported": contract.filters_supported,
            "dimensions_supported": contract.dimensions_supported,
            "causal_status": contract.causal_status,
            "caveats": contract.caveats,
            "allowed_visualizations": contract.allowed_visualizations,
        })

    return json.dumps({"METRIC_REGISTRY": registry_context}, indent=2)


def build_conversation_context(
    turns: List[Dict[str, Any]],
    max_turns: int = 5,
) -> str:
    """Build bounded conversation history for follow-up resolution.

    Only includes the last `max_turns` turns to control token usage.
    """
    if not turns:
        return ""

    recent_turns = turns[-max_turns:]
    context_lines = ["## CONVERSATION HISTORY (for follow-up resolution)"]

    for i, turn in enumerate(recent_turns, 1):
        query = turn.get("query", "")
        intent_type = turn.get("intent_type", "")
        metric = turn.get("primary_metric", "")
        district = turn.get("district", "")
        school_id = turn.get("school_id", "")

        context_lines.append(
            f"Turn {i}: Q=\"{query}\" | Intent={intent_type} | Metric={metric}"
            + (f" | District={district}" if district else "")
            + (f" | School={school_id}" if school_id else "")
        )

    return "\n".join(context_lines)


def build_evidence_context(
    query: str,
    intent_type: str,
    primary_metric: str,
    metric_label: str,
    evidence_records: List[Dict[str, Any]],
    methodology: Dict[str, Any],
    caveats: List[str],
    sample_size: int,
) -> str:
    """Build the verified evidence context block for Stage 2 answer synthesis.

    ONLY verified DuckDB evidence is included. The LLM must not introduce facts
    beyond what appears in this context.
    """
    lines = [
        f"QUESTION: {query}",
        f"INTENT: {intent_type}",
        f"PRIMARY_METRIC: {primary_metric} ({metric_label})",
        f"SAMPLE_SIZE: N = {sample_size}",
        "",
        "VERIFIED_DATA:",
        json.dumps(evidence_records[:15], indent=2, default=str),
        "",
        "METHODOLOGY:",
        json.dumps(methodology, indent=2, default=str),
        "",
        "CAVEATS:",
    ]
    for caveat in caveats:
        lines.append(f"- {caveat}")

    return "\n".join(lines)
