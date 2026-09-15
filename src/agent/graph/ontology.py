"""Formal semantic graph ontology for EduPulse AI Decision Intelligence Agent."""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Canonical domain entity types in EduPulse AI ontology."""

    SCHOOL = "school"
    DISTRICT = "district"
    BLOCK = "block"
    ASSESSMENT = "assessment"
    PROCUREMENT = "procurement"
    VENDOR = "vendor"
    COMMODITY = "commodity"
    METRIC = "metric"
    RISK = "risk"
    INTERVENTION = "intervention"
    AMENITY = "amenity"
    WELFARE_SEGMENT = "welfare_segment"
    QUALITY_GATE = "quality_gate"


class RelationType(str, Enum):
    """Canonical directional relationships connecting domain entities."""

    BELONGS_TO = "belongs_to"
    LOCATED_IN = "located_in"
    HAS_ATTENDANCE = "has_attendance"
    HAS_ASSESSMENT = "has_assessment"
    HAS_INFRASTRUCTURE = "has_infrastructure"
    HAS_PROCUREMENT = "has_procurement"
    HAS_RISK = "has_risk"
    HAS_INTERVENTION_PRIORITY = "has_intervention_priority"
    HAS_WELFARE_SEGMENT = "has_welfare_segment"
    HAS_DATA_QUALITY = "has_data_quality"
    MEASURED_BY = "measured_by"
    ASSOCIATED_WITH = "associated_with"
    SUPPLIED_BY = "supplied_by"
    INCLUDES_COMMODITY = "includes_commodity"
    SOURCED_FROM = "sourced_from"
    COMPOSED_OF = "composed_of"
    DRIVEN_BY = "driven_by"
    TARGETS = "targets"


class EntityNode(BaseModel):
    """A node in the analytical semantic graph."""

    entity_type: EntityType
    name: str
    description: str
    canonical_table: str
    identifier_column: str
    display_column: str
    attributes: List[str] = Field(default_factory=list)


class RelationEdge(BaseModel):
    """A directed edge in the analytical semantic graph."""

    source_type: EntityType
    relation: RelationType
    target_type: EntityType
    description: str
    join_key: str
    cardinality: str = "1:N"


class SemanticOntology:
    """Central semantic graph definition mapping education, infrastructure, and logistics."""

    def __init__(self) -> None:
        self.nodes: Dict[EntityType, EntityNode] = self._init_nodes()
        self.edges: List[RelationEdge] = self._init_edges()

    def _init_nodes(self) -> Dict[EntityType, EntityNode]:
        return {
            EntityType.SCHOOL: EntityNode(
                entity_type=EntityType.SCHOOL,
                name="School",
                description="Statutory primary, secondary, and higher secondary institutions.",
                canonical_table="dim_school",
                identifier_column="school_id",
                display_column="school_name",
                attributes=["district", "block", "school_type", "medium", "total_enrolled_students"],
            ),
            EntityType.DISTRICT: EntityNode(
                entity_type=EntityType.DISTRICT,
                name="District",
                description="Administrative educational administrative division (9 districts).",
                canonical_table="dim_district",
                identifier_column="district_key",
                display_column="district",
                attributes=["district", "total_schools", "total_enrolled"],
            ),
            EntityType.BLOCK: EntityNode(
                entity_type=EntityType.BLOCK,
                name="Block",
                description="Sub-district educational administrative cluster.",
                canonical_table="dim_block",
                identifier_column="block_key",
                display_column="block",
                attributes=["block", "district"],
            ),
            EntityType.METRIC: EntityNode(
                entity_type=EntityType.METRIC,
                name="Metric",
                description="Governed quantitative indicator computed from canonical warehouse views.",
                canonical_table="governed_metric_registry",
                identifier_column="metric_id",
                display_column="name",
                attributes=["source_view", "unit", "aggregation", "causal_status"],
            ),
            EntityType.RISK: EntityNode(
                entity_type=EntityType.RISK,
                name="Risk Severity",
                description="Observed vulnerability index (0-100) based on weighted deficits.",
                canonical_table="school_risk",
                identifier_column="school_id",
                display_column="risk_level",
                attributes=["risk_score", "attendance_risk", "academic_risk", "infrastructure_risk", "primary_risk_driver"],
            ),
            EntityType.INTERVENTION: EntityNode(
                entity_type=EntityType.INTERVENTION,
                name="Intervention Priority",
                description="Administrative action ordering index (0-100) for review triage.",
                canonical_table="school_intervention_priority",
                identifier_column="school_id",
                display_column="intervention_priority_tier",
                attributes=["intervention_priority_score", "district_attendance_gap", "district_academic_gap"],
            ),
            EntityType.AMENITY: EntityNode(
                entity_type=EntityType.AMENITY,
                name="Physical Infrastructure Amenity",
                description="5 core physical amenities preserving TRUE, FALSE, and UNKNOWN states.",
                canonical_table="school_welfare",
                identifier_column="school_id",
                display_column="infrastructure_readiness_pct",
                attributes=["electricity_status", "water_status", "toilet_status", "boundary_status", "playground_status"],
            ),
            EntityType.WELFARE_SEGMENT: EntityNode(
                entity_type=EntityType.WELFARE_SEGMENT,
                name="Welfare Quadrant",
                description="2x2 classification (Model, Resilient, Academic Intervention, Critical Intervention).",
                canonical_table="school_welfare_gap",
                identifier_column="school_id",
                display_column="welfare_quadrant",
                attributes=["welfare_quadrant", "quadrant_description"],
            ),
            EntityType.PROCUREMENT: EntityNode(
                entity_type=EntityType.PROCUREMENT,
                name="Procurement Exception",
                description="Mid-Day Meal expenditure records and peer 1.5 IQR benchmark exceptions.",
                canonical_table="procurement_summary",
                identifier_column="school_id",
                display_column="total_spend_inr",
                attributes=["total_spend_inr", "total_quantity_kg", "avg_cost_per_student", "is_procurement_outlier"],
            ),
            EntityType.QUALITY_GATE: EntityNode(
                entity_type=EntityType.QUALITY_GATE,
                name="Data Quality Gate",
                description="Automated boundary, parity, and consistency check ensuring analytical trust.",
                canonical_table="school_data_quality",
                identifier_column="school_id",
                display_column="data_quality_rate_pct",
                attributes=["trusted_records", "flagged_records", "excluded_from_metrics_count"],
            ),
        }

    def _init_edges(self) -> List[RelationEdge]:
        return [
            RelationEdge(
                source_type=EntityType.SCHOOL,
                relation=RelationType.BELONGS_TO,
                target_type=EntityType.DISTRICT,
                description="Each school operates in exactly one administrative district.",
                join_key="district",
                cardinality="N:1",
            ),
            RelationEdge(
                source_type=EntityType.SCHOOL,
                relation=RelationType.BELONGS_TO,
                target_type=EntityType.BLOCK,
                description="Each school operates in a sub-district educational block.",
                join_key="block",
                cardinality="N:1",
            ),
            RelationEdge(
                source_type=EntityType.SCHOOL,
                relation=RelationType.HAS_RISK,
                target_type=EntityType.RISK,
                description="Each school has a multi-factor risk severity score and driver taxonomy.",
                join_key="school_id",
                cardinality="1:1",
            ),
            RelationEdge(
                source_type=EntityType.SCHOOL,
                relation=RelationType.HAS_INTERVENTION_PRIORITY,
                target_type=EntityType.INTERVENTION,
                description="Each school has an administrative triage priority sequence score.",
                join_key="school_id",
                cardinality="1:1",
            ),
            RelationEdge(
                source_type=EntityType.SCHOOL,
                relation=RelationType.HAS_INFRASTRUCTURE,
                target_type=EntityType.AMENITY,
                description="Each school reports status for 5 statutory physical amenities.",
                join_key="school_id",
                cardinality="1:1",
            ),
            RelationEdge(
                source_type=EntityType.SCHOOL,
                relation=RelationType.HAS_WELFARE_SEGMENT,
                target_type=EntityType.WELFARE_SEGMENT,
                description="Each school is classified into a 2x2 physical-academic welfare quadrant.",
                join_key="school_id",
                cardinality="1:1",
            ),
            RelationEdge(
                source_type=EntityType.SCHOOL,
                relation=RelationType.HAS_PROCUREMENT,
                target_type=EntityType.PROCUREMENT,
                description="Each school has Mid-Day Meal delivery receipts and spend metrics.",
                join_key="school_id",
                cardinality="1:1",
            ),
            RelationEdge(
                source_type=EntityType.SCHOOL,
                relation=RelationType.HAS_DATA_QUALITY,
                target_type=EntityType.QUALITY_GATE,
                description="Each school tracks trusted vs flagged records across ingestion gates.",
                join_key="school_id",
                cardinality="1:1",
            ),
            RelationEdge(
                source_type=EntityType.RISK,
                relation=RelationType.DRIVEN_BY,
                target_type=EntityType.AMENITY,
                description="Infrastructure deficits directly contribute 20% to observed risk severity.",
                join_key="school_id",
                cardinality="1:1",
            ),
            RelationEdge(
                source_type=EntityType.INTERVENTION,
                relation=RelationType.TARGETS,
                target_type=EntityType.SCHOOL,
                description="Intervention queues schedule administrative reviews for vulnerable schools.",
                join_key="school_id",
                cardinality="1:1",
            ),
        ]

    def get_node(self, entity_type: EntityType) -> Optional[EntityNode]:
        return self.nodes.get(entity_type)

    def get_relations_from(self, source_type: EntityType) -> List[RelationEdge]:
        return [edge for edge in self.edges if edge.source_type == source_type]

    def get_relations_to(self, target_type: EntityType) -> List[RelationEdge]:
        return [edge for edge in self.edges if edge.target_type == target_type]


ontology = SemanticOntology()
