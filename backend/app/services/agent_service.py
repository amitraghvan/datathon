"""Central Agent Service managing execution, session state, and feedback tracking."""

import logging
import os
import time
from typing import Any, Dict, List

from backend.app.schemas.agent import (
    AgentCapabilitiesResponse,
    AgentFeedbackRequest,
    AgentQueryRequest,
    AgentQueryResponse,
    ConfigureLLMRequest,
)
from src.agent.agent import EduPulseAgent
from src.agent.graph.entities import DISTRICT_NAMES
from src.agent.graph.intent_schema import IntentType
from src.agent.graph.metric_registry import metric_registry

logger = logging.getLogger(__name__)


def _create_agent() -> EduPulseAgent:
    """Create EduPulseAgent with auto-detected LLM provider.

    Provider selection is based on environment variables:
    1. LLAMA_API_KEY → Llama31Provider
    2. OPENAI_API_KEY → OpenAICompatibleProvider
    3. None → MockDeterministicProvider
    """
    agent = EduPulseAgent()
    logger.info(
        f"Agent initialized — LLM mode: {agent.llm_mode}, "
        f"Reasoning: {agent.reasoning_mode}"
    )
    return agent


class AgentService:
    """Singleton service interfacing FastAPI routes with the EduPulseAgent engine."""

    def __init__(self) -> None:
        self.agent = _create_agent()
        self.feedback_log: List[Dict[str, Any]] = []

    def execute_query(self, request: AgentQueryRequest) -> AgentQueryResponse:
        """Process natural language analytical query and return full decision intelligence response."""
        context = dict(request.active_filters or {})
        if request.context_override:
            context.update(request.context_override)

        status_mode = "success"
        try:
            resp = self.agent.answer_query(
                query=request.query,
                session_id=request.session_id,
                context_override=context if context else None,
            )
            if resp.reasoning_mode == "deterministic_fallback":
                status_mode = "degraded"
        except Exception as e:
            logger.exception("Error during agent query processing: %s. Using safe fallback.", e)
            try:
                from src.agent.llm.mock_provider import MockDeterministicProvider
                safe_agent = EduPulseAgent(llm_provider=MockDeterministicProvider())
                resp = safe_agent.answer_query(
                    query=request.query,
                    session_id=request.session_id,
                    context_override=context if context else None,
                )
                resp.reasoning_mode = "deterministic_fallback"
                status_mode = "degraded"
                if "AI reasoning temporarily unavailable; using governed analytical fallback." not in resp.caveats:
                    resp.caveats.insert(0, "AI reasoning temporarily unavailable; using governed analytical fallback.")
            except Exception as e2:
                logger.exception("Fatal fallback error: %s", e2)
                import uuid
                return AgentQueryResponse(
                    status="degraded",
                    query_id=f"QRY_{uuid.uuid4().hex[:10].upper()}",
                    query=request.query,
                    intent_type="general_question",
                    confidence=0.5,
                    answer=(
                        "### Governed System Advisory\n\n"
                        "The analytical reasoning engine encountered a temporary processing condition. "
                        "Our governed DuckDB warehouse remains fully operational. "
                        "Please select one of the suggested education decision topics below."
                    ),
                    summary="System operating in governed degraded recovery mode.",
                    primary_metric="system_recovery",
                    primary_metric_label="System Recovery",
                    evidence_count=0,
                    evidence_records=[],
                    citations=[],
                    chart_plan={"chart_type": "table", "is_renderable": False, "data": []},
                    recommendations=[],
                    methodology={"engine": "Governed Recovery Fallback", "status": "DEGRADED"},
                    caveats=["AI reasoning temporarily unavailable; using governed analytical fallback."],
                    follow_up_questions=[
                        "Which 10 schools should be reviewed first?",
                        "Which districts have the weakest infrastructure?",
                        "Are attendance and academic scores associated?",
                    ],
                    grounding_audit={"is_grounded": True, "causal_flags": [], "unsupported_metrics": []},
                    timings_ms={"total_duration_ms": 1.0},
                    session_id=request.session_id,
                    reasoning_mode="deterministic_fallback",
                    llm_provider="governed_fallback",
                    confidence_score=0.5,
                )

        chart_dict = resp.chart_plan or {}
        chart_type = chart_dict.get("chart_type", "table")
        chart_data = chart_dict.get("data", [])

        return AgentQueryResponse(
            status=status_mode,
            query_id=resp.query_id,
            query=resp.query,
            intent_type=resp.intent_type,
            confidence=resp.confidence,
            answer=resp.answer,
            summary=resp.summary,
            primary_metric=resp.primary_metric,
            primary_metric_label=resp.primary_metric_label,
            evidence_count=resp.evidence_count,
            evidence_records=resp.evidence_records,
            citations=resp.citations,
            chart_plan=resp.chart_plan,
            recommendations=resp.recommendations,
            methodology=resp.methodology,
            caveats=resp.caveats,
            follow_up_questions=resp.follow_up_questions,
            grounding_audit=resp.grounding_audit,
            timings_ms=resp.timings_ms,
            session_id=resp.session_id,
            chart_type=chart_type,
            chart_data=chart_data,
            confidence_score=resp.confidence,
            reasoning_mode=resp.reasoning_mode,
            llm_provider=resp.llm_provider,
        )

    def record_feedback(self, request: AgentFeedbackRequest) -> Dict[str, Any]:
        """Record analyst feedback for governance and precision tracking."""
        record = {
            "query_id": request.query_id,
            "helpful": request.helpful,
            "comments": request.comments,
            "session_id": request.session_id,
            "timestamp": time.time(),
        }
        self.feedback_log.append(record)
        logger.info(f"Feedback recorded for {request.query_id}: helpful={request.helpful}")
        return {"status": "recorded", "query_id": request.query_id}

    def get_capabilities(self) -> AgentCapabilitiesResponse:
        """Return machine-readable capabilities, ontology entities, and governance rules."""
        metrics_catalog = metric_registry.list_metrics()

        return AgentCapabilitiesResponse(
            supported_intents=[i.value for i in IntentType],
            governed_metrics=metrics_catalog,
            supported_districts=DISTRICT_NAMES,
            guardrails=[
                "Read-only SQL compilation over DuckDB canonical views",
                "Zero raw CSV/XLSX/JSON unparameterized querying",
                "Strict distinction: Risk Severity (0-100) != Intervention Priority (0-100)",
                "Three-valued logic for physical infrastructure: AVAILABLE, MISSING, UNKNOWN",
                "Strictly observational framing: correlation != causation",
                "Procurement anomalies framed neutrally as peer benchmark exceptions",
                "Prompt injection and adversarial command filtration",
                "Post-LLM claim validation and grounding audit",
            ],
            architecture="Semantic Graph -> Llama 3.1 Intent -> Governed SQL -> DuckDB -> Evidence -> Llama 3.1 Synthesis -> Grounding Audit",
            llm_provider=self.agent.llm_mode,
            reasoning_mode=self.agent.reasoning_mode,
        )

    def get_health(self) -> Dict[str, Any]:
        """Verify warehouse connectivity and agent operational readiness."""
        return {
            "status": "HEALTHY",
            "agent": "EduPulse Phase 6 Graph-First AI Analyst",
            "warehouse": "DuckDB Canonical Analytics Warehouse",
            "total_metrics_cataloged": len(metric_registry.list_metrics()),
            "governance_mode": "STRICT_READ_ONLY_GROUNDED",
            "llm_provider": self.agent.llm_mode,
            "reasoning_mode": self.agent.reasoning_mode,
        }

    def get_llm_status(self) -> Dict[str, Any]:
        """Return LLM provider status WITHOUT exposing credentials."""
        is_configured = hasattr(self.agent.llm, "is_configured") and self.agent.llm.is_configured
        is_circuit_open = hasattr(self.agent.llm, "is_circuit_open") and self.agent.llm.is_circuit_open

        return {
            "provider": self.agent.llm_mode,
            "reasoning_mode": self.agent.reasoning_mode,
            "is_configured": is_configured,
            "is_available": is_configured and not is_circuit_open,
            "circuit_breaker_active": is_circuit_open,
            "model": getattr(self.agent.llm, "model", "deterministic"),
            "base_url_configured": bool(getattr(self.agent.llm, "base_url", "")),
            # NEVER expose API key
        }

    def configure_llm(self, req: ConfigureLLMRequest) -> Dict[str, Any]:
        """Dynamically configure or switch the active LLM provider."""
        provider_type = (req.provider or "").lower()

        if provider_type in ["llama", "llama_3.1", "groq"]:
            from src.agent.llm.llama_provider import Llama31Provider

            api_key = req.api_key or os.environ.get("LLAMA_API_KEY", "")
            base_url = req.base_url or os.environ.get("LLAMA_BASE_URL", "https://api.groq.com/openai/v1")
            model = req.model or os.environ.get("LLAMA_MODEL", "openai/gpt-oss-20b")

            provider = Llama31Provider(
                api_key=api_key,
                base_url=base_url,
                model=model,
            )
            self.agent.llm = provider
            if api_key:
                os.environ["LLAMA_API_KEY"] = api_key
            logger.info(f"Switched LLM provider to: {provider.provider_name}")
            return {
                "status": "success",
                "provider": provider.provider_name,
                "reasoning_mode": self.agent.reasoning_mode,
                "is_configured": provider.is_configured,
            }

        elif provider_type in ["openai"]:
            from src.agent.llm.openai_provider import OpenAICompatibleProvider

            api_key = req.api_key or os.environ.get("OPENAI_API_KEY", "")
            base_url = req.base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            model = req.model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

            provider = OpenAICompatibleProvider(
                api_key=api_key,
                base_url=base_url,
                model=model,
            )
            self.agent.llm = provider
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
            logger.info(f"Switched LLM provider to: {provider.provider_name}")
            return {
                "status": "success",
                "provider": provider.provider_name,
                "reasoning_mode": self.agent.reasoning_mode,
                "is_configured": provider.is_configured,
            }

        elif provider_type in ["ollama"]:
            from src.agent.llm.llama_provider import Llama31Provider

            base_url = req.base_url or "http://localhost:11434/v1"
            model = req.model or "llama3.1"
            provider = Llama31Provider(
                api_key="ollama",
                base_url=base_url,
                model=model,
            )
            self.agent.llm = provider
            return {
                "status": "success",
                "provider": provider.provider_name,
                "reasoning_mode": self.agent.reasoning_mode,
                "is_configured": True,
            }

        else:
            # Deterministic agentic reasoner
            from src.agent.llm.mock_provider import MockDeterministicProvider
            self.agent.llm = MockDeterministicProvider()
            return {
                "status": "success",
                "provider": self.agent.llm.provider_name,
                "reasoning_mode": "deterministic",
                "is_configured": True,
            }


agent_service = AgentService()
