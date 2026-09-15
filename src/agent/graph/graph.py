"""Semantic Graph engine unifying domain ontology, entities, and metric contracts."""

from typing import Any, Dict, List, Optional

from src.agent.graph.entities import resolve_entities
from src.agent.graph.intent_schema import AgentIntent, IntentType, classify_intent_heuristic
from src.agent.graph.metric_registry import metric_registry
from src.agent.graph.ontology import ontology
from src.agent.graph.relationships import CANONICAL_REASONING_PATHS, get_reasoning_path


class SemanticGraphEngine:
    """Analytical graph engine orchestrating entity-to-metric semantic resolution."""

    def __init__(self) -> None:
        self.ontology = ontology
        self.registry = metric_registry

    def parse_query_to_intent(self, query: str, context_filters: Optional[Dict[str, Any]] = None) -> AgentIntent:
        """Translate a natural language question into a validated AgentIntent."""
        entities = resolve_entities(query)
        intent_type = classify_intent_heuristic(query)

        # 1. Resolve primary target entity
        target_entity = "school"
        if "district" in query.lower() and not entities.school_ids:
            target_entity = "district"
        elif "block" in query.lower() and not entities.school_ids:
            target_entity = "block"
        elif "procurement" in query.lower() or "meal" in query.lower() or "vendor" in query.lower():
            target_entity = "procurement"
        elif "quality" in query.lower() or "trust" in query.lower() or "gate" in query.lower():
            target_entity = "quality_gate"

        # 2. Resolve primary metric
        metric_contract = self.registry.resolve_metric(query)
        metric_id = metric_contract.metric_id if metric_contract else "intervention_priority"

        # 3. Assemble active filters
        filters = dict(context_filters or {})
        if entities.districts:
            filters["district"] = entities.districts[0] if len(entities.districts) == 1 else entities.districts
        if entities.school_ids:
            filters["school_id"] = entities.school_ids[0] if len(entities.school_ids) == 1 else entities.school_ids
        if entities.missing_amenities:
            filters["missing_amenity"] = entities.missing_amenities[0]
            metric_id = "infrastructure_readiness_pct"
        elif entities.amenities:
            filters["amenity"] = entities.amenities[0]
            metric_id = "infrastructure_readiness_pct"
        if entities.quadrants:
            filters["welfare_quadrant"] = entities.quadrants[0]
        if entities.drivers:
            filters["primary_driver"] = entities.drivers[0]

        # 4. Determine dimensions
        dimensions = []
        if target_entity == "district" or "by district" in query.lower() or "across district" in query.lower():
            dimensions.append("district")
        if target_entity == "school":
            dimensions.append("school")

        limit = entities.limit or 10

        return AgentIntent(
            intent_type=intent_type,
            entity=target_entity,
            metric=metric_id,
            dimensions=dimensions,
            filters=filters,
            limit=limit,
            needs_explanation=(intent_type in [IntentType.DIAGNOSIS, IntentType.RECOMMENDATION]),
            raw_query=query,
            confidence=1.0,
        )

    def get_reasoning_lineage(self, intent: AgentIntent) -> List[Dict[str, Any]]:
        """Return graph traversal lineage demonstrating how conclusions are derived."""
        lineage: List[Dict[str, Any]] = []

        if intent.intent_type == IntentType.DIAGNOSIS:
            path = get_reasoning_path("intervention_diagnosis")
            if path:
                lineage = [
                    {
                        "step": i + 1,
                        "source": s.source.value,
                        "relation": s.relation.value,
                        "target": s.target.value,
                        "description": s.description,
                    }
                    for i, s in enumerate(path.steps)
                ]
        elif intent.entity == "district" or "district" in intent.dimensions:
            path = get_reasoning_path("district_welfare_audit")
            if path:
                lineage = [
                    {
                        "step": i + 1,
                        "source": s.source.value,
                        "relation": s.relation.value,
                        "target": s.target.value,
                        "description": s.description,
                    }
                    for i, s in enumerate(path.steps)
                ]
        elif intent.metric == "attendance_academic_correlation" or intent.intent_type == IntentType.ASSOCIATION:
            path = get_reasoning_path("attendance_academic_association")
            if path:
                lineage = [
                    {
                        "step": i + 1,
                        "source": s.source.value,
                        "relation": s.relation.value,
                        "target": s.target.value,
                        "description": s.description,
                    }
                    for i, s in enumerate(path.steps)
                ]
        elif intent.intent_type == IntentType.ANOMALY or "procurement" in intent.metric:
            path = get_reasoning_path("procurement_peer_exception")
            if path:
                lineage = [
                    {
                        "step": i + 1,
                        "source": s.source.value,
                        "relation": s.relation.value,
                        "target": s.target.value,
                        "description": s.description,
                    }
                    for i, s in enumerate(path.steps)
                ]
        else:
            # Default single-hop retrieval lineage
            lineage = [
                {
                    "step": 1,
                    "source": intent.entity,
                    "relation": "evaluated_under",
                    "target": intent.metric,
                    "description": f"Evaluate {intent.entity} using governed {intent.metric} contract.",
                }
            ]

        return lineage

    def get_capabilities_summary(self) -> Dict[str, Any]:
        """Return full semantic graph capabilities for introspection and API reflection."""
        return {
            "entity_types": [e.value for e in self.ontology.nodes.keys()],
            "relation_types": [r.relation.value for r in self.ontology.edges],
            "metrics": self.registry.list_metrics(),
            "reasoning_paths": [p.name for p in CANONICAL_REASONING_PATHS.values()],
        }


semantic_graph = SemanticGraphEngine()
