"""Relationship traversal rules and multi-hop reasoning paths for EduPulse AI semantic graph."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from src.agent.graph.ontology import EntityType, RelationType


class GraphPathStep(BaseModel):
    """A step in an analytical graph traversal path."""

    source: EntityType
    relation: RelationType
    target: EntityType
    description: str


class ReasoningPath(BaseModel):
    """A complete multi-hop reasoning sequence."""

    name: str
    description: str
    steps: List[GraphPathStep]
    policy_implication: str


# Pre-compiled canonical analytical reasoning paths
CANONICAL_REASONING_PATHS: Dict[str, ReasoningPath] = {
    "intervention_diagnosis": ReasoningPath(
        name="Intervention Priority Diagnosis",
        description="Decomposes administrative review priority into observable vulnerability drivers.",
        steps=[
            GraphPathStep(
                source=EntityType.SCHOOL,
                relation=RelationType.HAS_INTERVENTION_PRIORITY,
                target=EntityType.INTERVENTION,
                description="Retrieve school intervention priority score and review queue rank.",
            ),
            GraphPathStep(
                source=EntityType.INTERVENTION,
                relation=RelationType.COMPOSED_OF,
                target=EntityType.RISK,
                description="Extract multi-factor risk severity components (Attendance 45%, Academic 35%, Infra 20%).",
            ),
            GraphPathStep(
                source=EntityType.RISK,
                relation=RelationType.DRIVEN_BY,
                target=EntityType.AMENITY,
                description="Audit 5 statutory physical amenities (preserving TRUE, FALSE, UNKNOWN).",
            ),
            GraphPathStep(
                source=EntityType.INTERVENTION,
                relation=RelationType.TARGETS,
                target=EntityType.SCHOOL,
                description="Match dominant constraint to deterministic policy action catalog.",
            ),
        ],
        policy_implication="Guides targeted resource allocation without confusing review priority with critical risk severity.",
    ),
    "district_welfare_audit": ReasoningPath(
        name="District Welfare Disparity Audit",
        description="Analyzes educational performance against physical infrastructure readiness at district level.",
        steps=[
            GraphPathStep(
                source=EntityType.DISTRICT,
                relation=RelationType.LOCATED_IN,
                target=EntityType.SCHOOL,
                description="Aggregate all canonical schools operating within target district.",
            ),
            GraphPathStep(
                source=EntityType.SCHOOL,
                relation=RelationType.HAS_INFRASTRUCTURE,
                target=EntityType.AMENITY,
                description="Compute district physical infrastructure readiness percentage.",
            ),
            GraphPathStep(
                source=EntityType.SCHOOL,
                relation=RelationType.HAS_WELFARE_SEGMENT,
                target=EntityType.WELFARE_SEGMENT,
                description="Tally schools in Model, Resilient, and Critical Intervention quadrants.",
            ),
        ],
        policy_implication="Enables district education officers to prioritize capital expenditure where welfare gaps are largest.",
    ),
    "procurement_peer_exception": ReasoningPath(
        name="Procurement Peer Benchmark Review",
        description="Audits Mid-Day Meal delivery receipts and flags 1.5 IQR cost-per-student exceptions.",
        steps=[
            GraphPathStep(
                source=EntityType.SCHOOL,
                relation=RelationType.HAS_PROCUREMENT,
                target=EntityType.PROCUREMENT,
                description="Retrieve total spend, grain quantity (MT), and cost-per-pupil.",
            ),
            GraphPathStep(
                source=EntityType.PROCUREMENT,
                relation=RelationType.SOURCED_FROM,
                target=EntityType.METRIC,
                description="Evaluate spend against 1.5 IQR peer benchmark threshold (~₹350/pupil).",
            ),
        ],
        policy_implication="Identifies administrative anomalies requiring delivery batch review without leveling unsubstantiated fraud claims.",
    ),
    "attendance_academic_association": ReasoningPath(
        name="Attendance-Academic Observational Correlation",
        description="Evaluates student presence against foundational learning outcomes under observational governance.",
        steps=[
            GraphPathStep(
                source=EntityType.SCHOOL,
                relation=RelationType.HAS_ATTENDANCE,
                target=EntityType.METRIC,
                description="Compute weighted 30-day student attendance rate.",
            ),
            GraphPathStep(
                source=EntityType.SCHOOL,
                relation=RelationType.HAS_ASSESSMENT,
                target=EntityType.METRIC,
                description="Compute normalized foundational FLN academic score.",
            ),
        ],
        policy_implication="Documents positive co-occurrence (Pearson r = 0.453) while strictly disallowing causal claims.",
    ),
}


def get_reasoning_path(path_key: str) -> Optional[ReasoningPath]:
    """Retrieve pre-compiled reasoning path by key."""
    return CANONICAL_REASONING_PATHS.get(path_key)


def list_reasoning_paths() -> List[Dict[str, Any]]:
    """Return all available reasoning paths for capability introspection."""
    return [
        {
            "key": k,
            "name": p.name,
            "description": p.description,
            "step_count": len(p.steps),
            "policy_implication": p.policy_implication,
        }
        for k, p in CANONICAL_REASONING_PATHS.items()
    ]
