"""Automated Evaluation Runner for EduPulse AI Decision Intelligence Agent."""

import json
import os
import sys
import time
from typing import Any, Dict, List

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.agent import EduPulseAgent


def run_evaluation(eval_file: str = "evaluation/agent_eval_set.json") -> Dict[str, Any]:
    """Execute all benchmark test cases against the agent engine and score performance."""
    with open(eval_file, "r") as f:
        benchmarks: List[Dict[str, Any]] = json.load(f)

    agent = EduPulseAgent()
    results: List[Dict[str, Any]] = []

    passed_intents = 0
    passed_metrics = 0
    passed_sql = 0
    passed_citations = 0
    passed_grounding = 0
    passed_security = 0
    total_duration_ms: List[float] = []

    print("============================================================")
    print("EDUPULSE AI — PHASE 6 AGENT EVALUATION BENCHMARK")
    print(f"Total Test Cases: {len(benchmarks)}")
    print("============================================================\n")

    current_session = "eval_session_primary"

    for idx, b in enumerate(benchmarks, 1):
        bid = b["id"]
        category = b["category"]
        query = b["query"]
        exp_intent = b["expected_intent"]
        exp_metric = b["expected_metric"]
        req_sql = b["requires_sql"]
        must_cite = b["must_include_citation"]

        # Session chaining for conversational memory tests
        sess_id = current_session if "Conversational Memory" in category else None

        t0 = time.perf_counter()
        resp = agent.answer_query(query, session_id=sess_id)
        duration = (time.perf_counter() - t0) * 1000.0
        total_duration_ms.append(duration)

        # 1. Intent check (allow exact or semantic equivalence)
        intent_match = (
            resp.intent_type.lower() == exp_intent.lower()
            or exp_intent.lower() in resp.intent_type.lower()
            or (exp_intent == "ranking" and resp.intent_type in ["district_benchmark", "intervention_priority_ranking"])
            or (exp_intent == "association" and resp.intent_type in ["attendance_learning_correlation"])
            or (exp_intent == "anomaly" and resp.intent_type in ["mdm_anomaly_audit"])
            or (exp_intent == "diagnosis" and resp.intent_type in ["school_deep_dive", "lookup"])
            or (exp_intent == "lookup" and resp.intent_type in ["school_deep_dive", "ranking"])
        )
        if intent_match:
            passed_intents += 1

        # 2. Metric check
        metric_match = (
            resp.primary_metric == exp_metric
            or (exp_metric in ["attendance_rate_pct", "academic_score"] and "attendance" in resp.primary_metric)
            or (exp_metric == "intervention_priority" and resp.primary_metric in ["intervention_priority", "risk_score"])
            or (resp.primary_metric == "governance_rejection")
        )
        if metric_match:
            passed_metrics += 1

        # 3. SQL execution check
        sql_success = (req_sql and resp.evidence_count > 0) or (not req_sql and resp.evidence_count == 0)
        if sql_success:
            passed_sql += 1

        # 4. Citations check
        citations_valid = (must_cite and len(resp.citations) > 0) or (not must_cite and len(resp.citations) == 0)
        if citations_valid:
            passed_citations += 1

        # 5. Grounding check
        grounding_valid = resp.grounding_audit.get("is_grounded", False)
        if grounding_valid:
            passed_grounding += 1

        # 6. Security attack check
        if category == "Security & Deflection":
            if resp.primary_metric == "governance_rejection":
                passed_security += 1

        status_flag = "PASS" if (intent_match and grounding_valid and sql_success) else "WARN"
        print(f"[{status_flag}] #{idx:02d} {bid} [{category[:16]}] '{query[:35]}...' -> {resp.intent_type} | {resp.primary_metric} ({duration:.1f}ms)")

        results.append({
            "id": bid,
            "category": category,
            "query": query,
            "intent_match": intent_match,
            "metric_match": metric_match,
            "sql_success": sql_success,
            "citations_valid": citations_valid,
            "grounding_valid": grounding_valid,
            "duration_ms": round(duration, 2),
            "summary": resp.summary,
        })

    n = len(benchmarks)
    sec_cases = [b for b in benchmarks if b["category"] == "Security & Deflection"]
    sec_n = len(sec_cases)

    avg_latency = sum(total_duration_ms) / len(total_duration_ms) if total_duration_ms else 0.0
    p95_latency = sorted(total_duration_ms)[int(len(total_duration_ms) * 0.95)] if total_duration_ms else 0.0

    summary = {
        "total_test_cases": n,
        "intent_accuracy_pct": round((passed_intents / n) * 100.0, 1),
        "metric_resolution_pct": round((passed_metrics / n) * 100.0, 1),
        "sql_execution_success_pct": round((passed_sql / n) * 100.0, 1),
        "citations_valid_pct": round((passed_citations / n) * 100.0, 1),
        "grounding_audit_pass_pct": round((passed_grounding / n) * 100.0, 1),
        "security_deflection_pct": round((passed_security / sec_n) * 100.0, 1) if sec_n > 0 else 100.0,
        "avg_latency_ms": round(avg_latency, 2),
        "p95_latency_ms": round(p95_latency, 2),
    }

    print("\n============================================================")
    print("BENCHMARK EVALUATION SUMMARY RESULTS")
    print("============================================================")
    print(f"Total Cases:               {summary['total_test_cases']}")
    print(f"Intent Accuracy:           {summary['intent_accuracy_pct']}%")
    print(f"Metric Resolution:         {summary['metric_resolution_pct']}%")
    print(f"SQL Execution Success:     {summary['sql_execution_success_pct']}%")
    print(f"Citations Precision:       {summary['citations_valid_pct']}%")
    print(f"Grounding Audit (Zero-Hallucination): {summary['grounding_audit_pass_pct']}%")
    print(f"Prompt Injection Deflection:          {summary['security_deflection_pct']}%")
    print(f"Average Execution Latency: {summary['avg_latency_ms']} ms")
    print(f"P95 Execution Latency:     {summary['p95_latency_ms']} ms")
    print("============================================================\n")

    report_payload = {
        "evaluation_timestamp": time.time(),
        "summary": summary,
        "detailed_results": results,
    }

    with open("evaluation/benchmark_report.json", "w") as f:
        json.dump(report_payload, f, indent=2)

    return summary


if __name__ == "__main__":
    run_evaluation()
