"""OpenAI-compatible LLM Provider with graceful fallback to deterministic engine."""

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from src.agent.graph.graph import semantic_graph
from src.agent.graph.intent_schema import AgentIntent
from src.agent.grounding.evidence import EvidencePackage
from src.agent.llm.mock_provider import MockDeterministicProvider
from src.agent.llm.provider import LLMProvider
from src.agent.planner.planner import QueryPlan

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI and Ollama/vLLM compatible provider with offline deterministic fallback."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 8.0,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url or os.environ.get(
            "OPENAI_BASE_URL", "https://api.openai.com/v1"
        ).rstrip("/")
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout = timeout
        self.fallback = MockDeterministicProvider()

    @property
    def provider_name(self) -> str:
        """Human-readable provider identifier."""
        return f"openai_compatible ({self.model})"

    @property
    def is_configured(self) -> bool:
        """Check if an API key or local endpoint is configured."""
        return bool(self.api_key) or "localhost" in self.base_url or "127.0.0.1" in self.base_url

    def _call_chat_completions(self, messages: list, temperature: float = 0.0) -> Optional[str]:
        """Make synchronous HTTP call to chat completions API without external dependencies."""
        if not self.is_configured:
            return None

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 800,
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"External LLM API call failed ({e}); falling back to deterministic engine.")
            return None

    def parse_intent(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentIntent:
        """Parse natural language query using LLM if available, otherwise heuristic classifier."""
        # Always run deterministic semantic graph parser first as authoritative baseline
        heuristic_intent = semantic_graph.parse_query_to_intent(query, context)
        if not self.is_configured:
            return heuristic_intent

        system_prompt = (
            "You are an intent classifier for EduPulse AI. Given a user query, output a JSON object "
            "with keys: intent_type (one of: district_benchmark, school_deep_dive, mdm_anomaly_audit, "
            "attendance_learning_correlation, infrastructure_impact, intervention_priority_ranking, "
            "data_quality_diagnostic, retention_risk_overview, general_question), entities (school_id, "
            "district, metric_name, anomaly_type, min_score, limit), confidence (0.0 to 1.0)."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        resp = self._call_chat_completions(messages)
        if not resp:
            return heuristic_intent

        try:
            # Extract JSON block if surrounded by markdown
            clean_resp = resp.strip()
            if "```json" in clean_resp:
                clean_resp = clean_resp.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_resp:
                clean_resp = clean_resp.split("```")[1].split("```")[0].strip()

            parsed = json.loads(clean_resp)
            # Re-verify with heuristic entities to preserve canonical naming
            if "intent_type" in parsed:
                raw_intent = parsed.get("intent_type", heuristic_intent.intent_type.value)
                try:
                    from src.agent.graph.intent_schema import IntentType
                    intent_type = IntentType(raw_intent)
                except ValueError:
                    intent_type = heuristic_intent.intent_type

                entities = parsed.get("entities", {})
                filters = dict(heuristic_intent.filters)
                if isinstance(entities, dict):
                    filters.update(entities)

                return AgentIntent(
                    intent_type=intent_type,
                    entity=heuristic_intent.entity,
                    metric=heuristic_intent.metric,
                    dimensions=heuristic_intent.dimensions,
                    filters=filters,
                    limit=min(int(parsed.get("limit", heuristic_intent.limit)), 100),
                    confidence=min(float(parsed.get("confidence", 0.9)), 1.0),
                    raw_query=query,
                )
        except Exception:
            pass

        return heuristic_intent

    def recommend_chart_type(
        self,
        query: str,
        intent: AgentIntent,
        record_count: int,
    ) -> Optional[str]:
        """Recommend chart type via OpenAI completions if configured."""
        if not self.is_configured:
            return None

        prompt = (
            f"Query: {query}\n"
            f"Intent: {intent.intent_type.value}\n"
            f"Entity: {intent.entity}\n"
            f"Metric: {intent.metric}\n"
            f"Record Count: {record_count}\n"
            "Recommend the best chart type from: bar, horizontal_bar, line, scatter, heatmap, table, matrix, donut, kpi, none. "
            "Respond with ONLY the chart type name."
        )
        resp = self._call_chat_completions([{"role": "user", "content": prompt}], temperature=0.0)
        if resp:
            chart = resp.strip().lower().replace('"', "").replace("'", "")
            valid_types = {
                "bar", "horizontal_bar", "line", "scatter", "heatmap",
                "table", "matrix", "donut", "kpi", "none",
            }
            if chart in valid_types:
                return chart
        return None

    def synthesize_answer(
        self,
        query: str,
        evidence: EvidencePackage,
        plan: QueryPlan,
    ) -> str:
        """Synthesize response using LLM if available, falling back to deterministic synthesis."""
        if not self.is_configured:
            return self.fallback.synthesize_answer(query, evidence, plan)

        evidence_summary = [
            r for r in evidence.records[:10]
        ]
        system_prompt = (
            "You are the Lead Decision Intelligence Analyst for EduPulse AI Education Command Center.\n"
            "Generate an evidence-grounded answer following this STRICT executive structure:\n"
            "### Executive Finding\n<Clear 1-2 sentence high-level finding>\n\n"
            "### Diagnostic Drivers\n<Evidence-based root cause / comparative context>\n\n"
            "### Evidence & Citations\n<Specific figures citing the provided records>\n\n"
            "### Analytical Governance & Caveats\n<Observational vs causal caveats, 3-valued logic, sample sizes>\n\n"
            "### Recommended Action\n<Concrete operational next step>\n\n"
            "RULES:\n"
            "1. NEVER claim attendance causes FLN scores. Use observational correlation phrasing.\n"
            "2. NEVER invent numbers not in the evidence records.\n"
            "3. NEVER frame procurement outliers as fraud; use 'peer benchmark exceptions'.\n"
            "4. NEVER treat UNKNOWN infrastructure as FALSE."
        )

        user_content = (
            f"User Query: {query}\n"
            f"Intent: {plan.intent.intent_type.value}\n"
            f"Primary Metric: {plan.primary_metric}\n"
            f"Sample Size: N = {evidence.record_count}\n"
            f"Evidence Records: {json.dumps(evidence_summary, default=str)}\n"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
        resp = self._call_chat_completions(messages, temperature=0.1)
        if resp and len(resp.strip()) > 100:
            return resp.strip()

        return self.fallback.synthesize_answer(query, evidence, plan)
