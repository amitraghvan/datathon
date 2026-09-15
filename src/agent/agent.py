"""Master Agent Engine for EduPulse AI Education Welfare Command Center.

Implements the governed two-stage LLM architecture:
  Stage 1: User question → LLM → AgentIntent → Pydantic → Metric Registry → DuckDB
  Stage 2: Verified evidence → LLM → Grounded narrative → Claim validation

The LLM (Llama 3.1) is responsible for language understanding and synthesis ONLY.
DuckDB, the metric registry, and the deterministic query planner remain authoritative.
"""

import logging
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.agent.execution.executor import GovernedExecutor
from src.agent.execution.sql_guard import SQLGuard
from src.agent.graph.graph import SemanticGraphEngine
from src.agent.graph.intent_schema import AgentIntent, IntentType
from src.agent.grounding.citations import generate_citations
from src.agent.grounding.evidence import EvidencePackage, package_evidence
from src.agent.grounding.validator import validate_llm_answer
from src.agent.llm.mock_provider import MockDeterministicProvider
from src.agent.llm.provider import LLMProvider
from src.agent.memory.conversation import ConversationManager
from src.agent.planner.planner import DeterministicQueryPlanner
from src.agent.security.injection_guard import sanitize_and_check_injection
from src.agent.synthesis.recommender import generate_recommendations
from src.agent.visualization.chart_planner import plan_chart_intent

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Comprehensive, consulting-grade analytical response model."""

    query_id: str
    query: str
    intent_type: str
    confidence: float
    answer: str
    summary: str
    primary_metric: str
    primary_metric_label: str
    evidence_count: int
    evidence_records: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    chart_plan: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    methodology: Dict[str, Any]
    caveats: List[str]
    follow_up_questions: List[str]
    grounding_audit: Dict[str, Any]
    timings_ms: Dict[str, float]
    session_id: Optional[str] = None
    reasoning_mode: str = "deterministic"
    llm_provider: str = "mock_deterministic"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize full response for API transmission."""
        return {
            "query_id": self.query_id,
            "query": self.query,
            "intent_type": self.intent_type,
            "confidence": self.confidence,
            "answer": self.answer,
            "summary": self.summary,
            "primary_metric": self.primary_metric,
            "primary_metric_label": self.primary_metric_label,
            "evidence_count": self.evidence_count,
            "evidence_records": self.evidence_records,
            "citations": self.citations,
            "chart_plan": self.chart_plan,
            "recommendations": self.recommendations,
            "methodology": self.methodology,
            "caveats": self.caveats,
            "follow_up_questions": self.follow_up_questions,
            "grounding_audit": self.grounding_audit,
            "timings_ms": self.timings_ms,
            "session_id": self.session_id,
            "reasoning_mode": self.reasoning_mode,
            "llm_provider": self.llm_provider,
        }


def _create_llm_provider() -> LLMProvider:
    """Auto-detect and instantiate the best available LLM provider.

    Priority:
    1. Llama 3.1 (if LLAMA_API_KEY is set)
    2. OpenAI-compatible (if OPENAI_API_KEY is set)
    3. MockDeterministicProvider (always available, zero-credential)
    """
    # Try Llama 3.1 first
    llama_key = os.environ.get("LLAMA_API_KEY", "")
    if llama_key:
        try:
            from src.agent.llm.llama_provider import Llama31Provider
            provider = Llama31Provider()
            logger.info(f"LLM Provider: {provider.provider_name}")
            return provider
        except Exception as e:
            logger.warning(f"Failed to initialize Llama31Provider: {e}")

    # Try OpenAI-compatible
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if openai_key:
        try:
            from src.agent.llm.openai_provider import OpenAICompatibleProvider
            provider = OpenAICompatibleProvider()
            if provider.is_configured:
                logger.info(f"LLM Provider: {provider.provider_name}")
                return provider
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAICompatibleProvider: {e}")

    # Deterministic fallback — always works
    logger.info("LLM Provider: MockDeterministicProvider (no credentials detected)")
    return MockDeterministicProvider()


class EduPulseAgent:
    """Enterprise Graph-First AI Decision Intelligence Agent."""

    def __init__(
        self,
        db_path: str = "warehouse/edupulse.duckdb",
        llm_provider: Optional[LLMProvider] = None,
        use_openai_if_available: bool = True,
    ):
        self.db_path = db_path
        self.graph = SemanticGraphEngine()
        self.planner = DeterministicQueryPlanner(self.graph)
        self.sql_guard = SQLGuard()
        self.executor = GovernedExecutor()
        self.memory = ConversationManager()

        if llm_provider:
            self.llm = llm_provider
        else:
            self.llm = _create_llm_provider()

    @property
    def llm_mode(self) -> str:
        """Report current LLM provider type."""
        return getattr(self.llm, "provider_name", "unknown")

    @property
    def reasoning_mode(self) -> str:
        """Report reasoning mode for API responses."""
        name = self.llm_mode
        if "llama" in name.lower():
            # Check if circuit breaker is active
            if hasattr(self.llm, "is_circuit_open") and self.llm.is_circuit_open:
                return "deterministic_fallback"
            return "llama_3.1"
        if "openai" in name.lower():
            return "openai_compatible"
        return "deterministic"

    def _generate_follow_ups(self, intent: AgentIntent, evidence: EvidencePackage) -> List[str]:
        """Generate context-aware follow-up question recommendations."""
        records = evidence.records
        itype = intent.intent_type

        if itype == IntentType.DISTRICT_BENCHMARK:
            if records:
                top_dist = records[0].get("district", "the top district")
                bottom_dist = records[-1].get("district", "the lowest district")
                return [
                    f"Show me the top 5 schools requiring intervention in {bottom_dist}",
                    f"What are the primary infrastructure gaps in {top_dist}?",
                    "How does attendance correlate with FLN scores across all districts?",
                ]
            return [
                "Which district has the lowest attendance rate?",
                "What is the statewide FLN distribution across rural vs urban schools?",
            ]

        if itype in [IntentType.SCHOOL_DEEP_DIVE, IntentType.INTERVENTION_PRIORITY_RANKING]:
            if records:
                sch_id = records[0].get("school_id", "this school")
                dist = records[0].get("district", "its district")
                return [
                    f"What specific amenities are missing or unverified at {sch_id}?",
                    f"Compare {sch_id} against the average performance in {dist}",
                    "What recommended operational interventions apply to this school?",
                ]
            return [
                "Show me the top 10 schools in the intervention priority queue",
                "Which schools have critical retention risk scores exceeding 70?",
            ]

        if itype == IntentType.MDM_ANOMALY_AUDIT:
            return [
                "Which supplier batches contributed to the highest cost variances?",
                "Are these procurement exceptions concentrated in specific rural districts?",
                "What is the recommended supplier reconciliation protocol?",
            ]

        if itype == IntentType.ATTENDANCE_LEARNING_CORRELATION:
            return [
                "Does the attendance correlation hold for both primary and secondary schools?",
                "How do schools with complete electrification perform on FLN outcomes?",
                "Show me schools with high attendance but low academic scores",
            ]

        return [
            "Which districts show the largest welfare support gap?",
            "What is the current profile completeness across all 600 schools?",
            "List the top 5 schools with highest intervention priority",
        ]

    def answer_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        context_override: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Execute full Graph-First Decision Intelligence pipeline for a user question."""
        t_start = time.perf_counter()
        query_id = f"QRY_{uuid.uuid4().hex[:10].upper()}"
        timings: Dict[str, float] = {}

        # Track current reasoning mode
        current_reasoning_mode = self.reasoning_mode
        current_llm_provider = self.llm_mode

        # 1. Security & Prompt Injection Check
        sec_result = sanitize_and_check_injection(query)
        if not sec_result.is_safe:
            duration = (time.perf_counter() - t_start) * 1000.0
            return AgentResponse(
                query_id=query_id,
                query=query,
                intent_type=IntentType.GENERAL_QUESTION.value,
                confidence=1.0,
                answer=(
                    "### Security & Governance Advisory\n\n"
                    f"Your request could not be processed: **{sec_result.reason}**\n\n"
                    "EduPulse AI adheres to strict data governance boundaries. All analytical queries "
                    "must target governed educational entities (districts, schools, commodities) and metrics "
                    "without unparameterized SQL, instruction tampering, or system prompt modifications."
                ),
                summary="Query rejected by governance and prompt injection guard.",
                primary_metric="governance_rejection",
                primary_metric_label="Governance Guard",
                evidence_count=0,
                evidence_records=[],
                citations=[],
                chart_plan={"chart_type": "table", "is_renderable": False, "data": []},
                recommendations=[],
                methodology={"governance": "Prompt Injection Guard", "status": "REJECTED"},
                caveats=["Security enforcement triggered: Prohibited pattern detected."],
                follow_up_questions=[
                    "Which district has the lowest attendance rate?",
                    "Show the top 5 schools requiring intervention",
                    "What is the correlation between attendance and FLN score?",
                ],
                grounding_audit={"is_grounded": True, "causal_flags": [], "unsupported_metrics": []},
                timings_ms={"total_duration_ms": round(duration, 2), "sql_duration_ms": 0.0},
                session_id=session_id,
                reasoning_mode=current_reasoning_mode,
                llm_provider=current_llm_provider,
            )

        sanitized_query = sec_result.sanitized_query

        # 1.5 Conversational Greeting & Assistance Fast-Path
        q_norm = sanitized_query.strip().lower().rstrip("?!.,")
        GREETING_TOKENS = {
            "hi", "hii", "hiii", "hello", "hey", "namaste", "hola", "salam",
            "good morning", "good afternoon", "good evening",
            "who are you", "what can you do", "help", "kya kar sakte ho", "help me"
        }
        if q_norm in GREETING_TOKENS or q_norm.startswith(("hi ", "hello ", "hey ")):
            duration = (time.perf_counter() - t_start) * 1000.0
            return AgentResponse(
                query_id=query_id,
                query=query,
                intent_type="general_question",
                confidence=1.0,
                answer=(
                    "### Welcome to EduPulse AI — Decision Intelligence Copilot\n\n"
                    "Hello! I am your AI analyst connected directly to the **Punjab Education Welfare Analytics Warehouse** (DuckDB).\n\n"
                    "I can answer analytical questions about:\n"
                    "- **Student Attendance**: District rankings, attendance trends, temporal stability.\n"
                    "- **Academic Performance**: FLN scores, subject outcomes, correlation with attendance ($r = 0.453$).\n"
                    "- **School Welfare & Amenities**: 2×2 Welfare Gap analysis, statutory amenities (electricity, water, toilets).\n"
                    "- **MDM Nutritional Welfare**: Mid-Day Meal spend distribution, commodity pricing, peer benchmark exceptions.\n"
                    "- **Intervention Prioritization**: Actionable priority review queues (0–100) and risk driver diagnosis.\n\n"
                    "**Try asking me:**\n"
                    "- *\"Which district has the lowest attendance rate?\"*\n"
                    "- *\"Show me the top 5 schools requiring immediate intervention.\"*\n"
                    "- *\"Does student attendance correlate with FLN academic scores?\"*\n"
                    "- *\"Why is SCH0386 marked as high priority?\"*"
                ),
                summary="EduPulse AI Decision Intelligence Copilot is ready to analyze educational metrics.",
                primary_metric="intervention_priority",
                primary_metric_label="Intervention Priority",
                evidence_count=0,
                evidence_records=[],
                citations=[],
                chart_plan={"chart_type": "table", "is_renderable": False, "data": []},
                recommendations=[],
                methodology={"governance": "Conversational Copilot Routine", "status": "ACTIVE"},
                caveats=[],
                follow_up_questions=[
                    "Which district has the lowest attendance rate?",
                    "Show the top 5 schools requiring intervention",
                    "Does attendance correlate with FLN scores?",
                ],
                grounding_audit={"is_grounded": True, "unverified_numbers": [], "causal_violations": [], "unverified_entities": []},
                timings_ms={"total_duration_ms": round(duration, 2), "sql_duration_ms": 0.0},
                session_id=session_id,
                reasoning_mode=current_reasoning_mode,
                llm_provider=current_llm_provider,
            )

        # 1.6 Domain Boundary & Out-of-Scope Protection
        UNSUPPORTED_DOMAINS = [
            "random data", "not available", "weather", "cricket", "football",
            "recipe", "joke", "tell me a story", "song", "who is the president",
            "stock price", "bitcoin", "tell me something not"
        ]
        if any(w in q_norm for w in UNSUPPORTED_DOMAINS):
            duration = (time.perf_counter() - t_start) * 1000.0
            return AgentResponse(
                query_id=query_id,
                query=query,
                intent_type="general_question",
                confidence=1.0,
                answer=(
                    "### Analytical Scope & Domain Boundary\n\n"
                    "The requested topic is outside the analytical boundaries of the **EduPulse AI Education Welfare Warehouse**.\n\n"
                    "EduPulse AI is strictly governed to provide verifiable intelligence on:\n"
                    "- **Student Attendance & Trends** (`dim_school`, `school_performance`)\n"
                    "- **Academic FLN Scores & Correlations** (`fact_assessment`)\n"
                    "- **Physical Amenities & Infrastructure Readiness** (`school_welfare`)\n"
                    "- **Mid-Day Meal Nutritional Procurement** (`procurement_summary`)\n"
                    "- **Intervention Prioritization & Risk Deficits** (`school_intervention_priority`)\n"
                    "- **Data Quality & Ten Quality Gates** (`school_data_quality`)\n\n"
                    "Please submit inquiries targeting verified educational entities, district benchmarks, or intervention queues."
                ),
                summary="Query outside educational domain; safely deflected under governance policy.",
                primary_metric="domain_boundary",
                primary_metric_label="Domain Boundary",
                evidence_count=0,
                evidence_records=[],
                citations=[],
                chart_plan={"chart_type": "table", "is_renderable": False, "data": []},
                recommendations=[],
                methodology={"governance": "Domain Boundary Enforcement", "status": "OUT_OF_SCOPE"},
                caveats=["Requests outside educational operations are rejected to prevent hallucination."],
                follow_up_questions=[
                    "Which 10 schools should be reviewed first?",
                    "Which districts have the weakest infrastructure?",
                    "Are attendance and academic scores associated?",
                ],
                grounding_audit={"is_grounded": True, "unverified_numbers": [], "causal_violations": [], "unverified_entities": []},
                timings_ms={"total_duration_ms": round(duration, 2), "sql_duration_ms": 0.0},
                session_id=session_id,
                reasoning_mode=current_reasoning_mode,
                llm_provider=current_llm_provider,
            )

        # 2. Session Context Injection
        session = self.memory.get_session(session_id) if session_id else None
        session_context = session.resolve_context(sanitized_query) if session else {}
        if context_override:
            session_context.update(context_override)

        # 3. Intent Parsing & Entity Extraction (STAGE 1 — LLM Planning)
        t_intent_start = time.perf_counter()
        intent = self.llm.parse_intent(sanitized_query, context=session_context)
        timings["intent_duration_ms"] = round((time.perf_counter() - t_intent_start) * 1000.0, 2)

        # 4. Semantic Query Planning (DETERMINISTIC — always authoritative)
        t_plan_start = time.perf_counter()
        plan = self.planner.plan(intent)
        timings["planning_duration_ms"] = round((time.perf_counter() - t_plan_start) * 1000.0, 2)

        # 5. Governed Execution via DuckDB (SOURCE OF TRUTH)
        t_exec_start = time.perf_counter()
        exec_result = self.executor.execute(plan)
        timings["sql_duration_ms"] = round(exec_result.sql_duration_ms, 2)
        timings["execution_duration_ms"] = round((time.perf_counter() - t_exec_start) * 1000.0, 2)

        # 6. Evidence Packaging & Citations
        t_ev_start = time.perf_counter()
        evidence = package_evidence(plan, exec_result.records)
        citations = generate_citations(plan, evidence)
        timings["evidence_duration_ms"] = round((time.perf_counter() - t_ev_start) * 1000.0, 2)

        # 7. Synthesis & Narrative Generation (STAGE 2 — LLM Synthesis)
        t_synth_start = time.perf_counter()
        narrative = self.llm.synthesize_answer(sanitized_query, evidence, plan)
        timings["synthesis_duration_ms"] = round((time.perf_counter() - t_synth_start) * 1000.0, 2)

        # 8. Grounding & Anti-Hallucination Audit (POST-LLM VALIDATION)
        t_ground_start = time.perf_counter()
        grounding_audit = validate_llm_answer(narrative, evidence, plan)

        # If LLM answer fails grounding and we have a Llama provider, attempt repair
        if not grounding_audit.is_grounded and hasattr(self.llm, "synthesize_with_repair"):
            logger.info(
                f"Grounding validation failed: {grounding_audit.validation_issues_summary}. "
                "Attempting LLM repair synthesis..."
            )
            repaired_narrative = self.llm.synthesize_with_repair(
                sanitized_query, evidence, plan,
                failed_answer=narrative,
                validation_issues=grounding_audit.validation_issues_summary,
            )
            repair_audit = validate_llm_answer(repaired_narrative, evidence, plan)

            if repair_audit.is_grounded:
                narrative = repaired_narrative
                grounding_audit = repair_audit
                logger.info("LLM repair synthesis PASSED grounding validation.")
            else:
                # Final fallback — use deterministic answer
                logger.warning(
                    "LLM repair synthesis also failed grounding. "
                    "Falling back to deterministic narrative."
                )
                fallback = MockDeterministicProvider()
                narrative = fallback.synthesize_answer(sanitized_query, evidence, plan)
                grounding_audit = validate_llm_answer(narrative, evidence, plan)
                grounding_audit.fallback_applied = True
                current_reasoning_mode = "deterministic_fallback"

        timings["grounding_duration_ms"] = round((time.perf_counter() - t_ground_start) * 1000.0, 2)

        # Append cautionary note if ungrounded claims or causal phrasing detected
        if not grounding_audit.is_grounded:
            narrative += (
                f"\n\n> [!CAUTION]\n> **Grounding Integrity Warning**: {grounding_audit.details}"
            )

        # 9. Dynamic Visualization Planning
        chart_rec = None
        if hasattr(self.llm, "recommend_chart_type"):
            try:
                chart_rec = self.llm.recommend_chart_type(sanitized_query, intent, evidence.record_count)
            except Exception as e:
                logger.debug(f"LLM chart recommendation failed: {e}")
        chart_plan = plan_chart_intent(intent, evidence, chart_recommendation=chart_rec)

        # 10. Operational Action Recommendations
        recommendations = generate_recommendations(intent, evidence)

        # 11. Extract Summary Headline (first 2 sentences or Executive Finding block)
        summary = ""
        if "### Executive Finding" in narrative:
            parts = narrative.split("### Executive Finding")[1].split("###")[0].strip()
            summary = parts.split("\n")[0].strip()
        else:
            summary = narrative.split("\n\n")[0].replace("#", "").strip()[:200]

        # 12. Follow-Up Questions
        follow_ups = self._generate_follow_ups(intent, evidence)

        # 13. Update Conversational Memory
        if session:
            session.add_turn(
                query=sanitized_query,
                intent=intent,
                answer=narrative,
                primary_metric=plan.primary_metric,
                records=evidence.records,
            )

        timings["total_duration_ms"] = round((time.perf_counter() - t_start) * 1000.0, 2)

        return AgentResponse(
            query_id=query_id,
            query=sanitized_query,
            intent_type=intent.intent_type.value,
            confidence=intent.confidence,
            answer=narrative,
            summary=summary,
            primary_metric=plan.primary_metric,
            primary_metric_label=plan.metric_meta.label,
            evidence_count=evidence.record_count,
            evidence_records=evidence.records[:50],  # Return up to 50 for client table rendering
            citations=[c.to_dict() for c in citations],
            chart_plan=chart_plan.to_dict(),
            recommendations=[r.to_dict() for r in recommendations],
            methodology=plan.to_dict()["methodology"],
            caveats=list(set(plan.metric_meta.caveat_list + (["Strictly observational correlation"] if plan.metric_meta.is_observational_only else []))),
            follow_up_questions=follow_ups,
            grounding_audit=grounding_audit.to_dict(),
            timings_ms=timings,
            session_id=session_id,
            reasoning_mode=current_reasoning_mode,
            llm_provider=current_llm_provider,
        )
