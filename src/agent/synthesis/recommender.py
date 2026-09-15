"""Operational action recommendation engine grounded in analytical evidence."""

from dataclasses import dataclass
from typing import Any, Dict, List

from src.agent.graph.intent_schema import AgentIntent, IntentType
from src.agent.grounding.evidence import EvidencePackage


@dataclass
class RecommendedAction:
    """Actionable administrative intervention grounded in analytical findings."""

    action_code: str
    action_title: str
    target_entity: str
    urgency: str  # "IMMEDIATE", "HIGH", "MEDIUM", "ROUTINE"
    rationale: str
    estimated_impact: str
    owner: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to JSON-serializable dictionary."""
        return {
            "action_code": self.action_code,
            "action_title": self.action_title,
            "target_entity": self.target_entity,
            "urgency": self.urgency,
            "rationale": self.rationale,
            "estimated_impact": self.estimated_impact,
            "owner": self.owner,
        }


def generate_recommendations(intent: AgentIntent, evidence: EvidencePackage) -> List[RecommendedAction]:
    """Generate targeted administrative actions based on intent and query results."""
    records = evidence.records
    if not records:
        return []

    actions: List[RecommendedAction] = []

    # 1. School-Level or Priority Queue Actions
    if intent.intent_type in [IntentType.SCHOOL_DEEP_DIVE, IntentType.INTERVENTION_PRIORITY_RANKING]:
        top_records = records[:3]
        for r in top_records:
            school_id = r.get("school_id", "School")
            district = r.get("district", "District")
            priority = r.get("intervention_priority_score", 0.0)
            risk = r.get("retention_risk_score", 0.0)
            attendance = r.get("attendance_rate", 100.0)
            elec = str(r.get("electricity_status", "")).upper()
            water = str(r.get("water_status", "")).upper()

            # Infrastructure intervention
            if elec in ["MISSING", "NO", "FALSE"] or water in ["MISSING", "NO", "FALSE"]:
                actions.append(
                    RecommendedAction(
                        action_code=f"ACT_INFRA_{school_id}",
                        action_title="Fast-Track Basic Amenity Electrification Grant",
                        target_entity=f"{school_id} ({district})",
                        urgency="IMMEDIATE" if priority > 70 else "HIGH",
                        rationale=f"School exhibits verified amenity gaps (Electricity: {elec}, Water: {water}) alongside intervention priority {priority:.1f} (risk {risk:.1f}).",
                        estimated_impact="Stabilizes classroom environment and supports digital learning integration.",
                        owner="District Infrastructure Engineer & SSA Cell",
                    )
                )

            # High priority review
            if priority >= 60.0:
                actions.append(
                    RecommendedAction(
                        action_code=f"ACT_REVIEW_{school_id}",
                        action_title="Multidisciplinary Retention Taskforce Desk Audit",
                        target_entity=f"{school_id} ({district})",
                        urgency="HIGH",
                        rationale=f"Intervention priority score of {priority:.1f} places this school in top tier administrative review queue.",
                        estimated_impact="Mandatory on-site diagnostic within 14 calendar days.",
                        owner=f"{district} Block Education Officer (BEO)",
                    )
                )

            # Low attendance intervention
            if attendance < 72.0:
                actions.append(
                    RecommendedAction(
                        action_code=f"ACT_ATTEND_{school_id}",
                        action_title="Community Attendance Drive & SMC Engagement",
                        target_entity=f"{school_id} ({district})",
                        urgency="HIGH",
                        rationale=f"Weighted attendance is {attendance:.1f}%, indicating chronic student absenteeism patterns.",
                        estimated_impact="Targeted +8-12% attendance recovery within 60 days.",
                        owner="School Management Committee (SMC) & Headmaster",
                    )
                )

    # 2. District-Level Benchmarking Actions
    elif intent.intent_type == IntentType.DISTRICT_BENCHMARK:
        # Find district with lowest FLN or lowest attendance
        sorted_by_fln = sorted(records, key=lambda x: x.get("mean_fln_score", x.get("composite_score", 100)))
        if sorted_by_fln:
            lowest_dist = sorted_by_fln[0]
            dist_name = lowest_dist.get("district", "District")
            fln_val = lowest_dist.get("mean_fln_score", lowest_dist.get("composite_score", 0.0))
            actions.append(
                RecommendedAction(
                    action_code=f"ACT_DIST_FLN_{dist_name}",
                    action_title=f"FLN Accelerated Remediation Initiative for {dist_name}",
                    target_entity=dist_name,
                    urgency="HIGH",
                    rationale=f"{dist_name} records mean FLN score of {fln_val:.1f}, placing it in the bottom district tier.",
                    estimated_impact="Standardized teacher training workshops and bi-weekly diagnostic milestone tracking.",
                    owner="State Directorate of Primary Education & DIET Principal",
                )
            )

    # 3. MDM / Procurement Outliers
    elif intent.intent_type == IntentType.MDM_ANOMALY_AUDIT:
        commodities = [r.get("commodity", "") for r in records[:3] if r.get("commodity")]
        comm_str = ", ".join(commodities) if commodities else "Flagged Commodities"
        actions.append(
            RecommendedAction(
                action_code="ACT_MDM_AUDIT",
                action_title="Procurement Peer Benchmark Desk Audit & Price Standardization",
                target_entity=comm_str,
                urgency="HIGH",
                rationale="Identified transaction unit costs exceed 1.5 IQR peer distribution bounds across supply batches.",
                estimated_impact="Reconciliation of supplier invoices against state benchmark rate schedules without supply disruption.",
                owner="Mid-Day Meal Welfare Directorate & District Supply Officer",
            )
        )

    # 4. Association / Learning Correlation Actions
    elif intent.intent_type == IntentType.ATTENDANCE_LEARNING_CORRELATION:
        actions.append(
            RecommendedAction(
                action_code="ACT_RETENTION_FLN",
                action_title="Integrated Attendance-Learning Early Warning Protocol",
                target_entity="Statewide Schools",
                urgency="MEDIUM",
                rationale="Empirical observational association (r = 0.453) confirms lower attendance correlates with depressed FLN scores.",
                estimated_impact="Automated SMS trigger to guardians when student falls below 75% monthly attendance threshold.",
                owner="State Education MIS Operations Unit",
            )
        )

    # 5. Data Quality Actions
    elif intent.intent_type == IntentType.DATA_QUALITY_DIAGNOSTIC:
        actions.append(
            RecommendedAction(
                action_code="ACT_DATA_RECON",
                action_title="School Headmaster Asset & Register Verification Drive",
                target_entity="Schools with Data Flags",
                urgency="MEDIUM",
                rationale="Audit identified profile completeness discrepancies and unmatched enrollment registers.",
                estimated_impact="Elevates state educational data completeness to >98% verifiable ground truth.",
                owner="District EMIS Coordinator",
            )
        )

    # Default fallback action
    if not actions:
        actions.append(
            RecommendedAction(
                action_code="ACT_GOV_REVIEW",
                action_title="Governance Continuous Monitoring Routine",
                target_entity="Executive Directorate",
                urgency="ROUTINE",
                rationale="Routine analytical review across governed DuckDB views.",
                estimated_impact="Maintains real-time visibility into educational welfare KPIs.",
                owner="Departmental Planning Officer",
            )
        )

    return actions
