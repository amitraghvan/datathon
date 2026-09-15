"""Governed execution engine with SQL safety, timeouts, and latency instrumentation."""

import time
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from backend.app.repository.duckdb import db_repo
from src.agent.execution.sql_guard import validate_sql_safety
from src.agent.planner.planner import QueryPlan


class ExecutionResult(BaseModel):
    """Result of safe DuckDB query execution with timing metadata."""

    records: List[Dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    sql_duration_ms: float = 0.0
    view_used: str = ""
    is_empty: bool = False
    plan: QueryPlan


class GovernedExecutor:
    """Safe executor interfacing with DuckDB warehouse."""

    def __init__(self, repo=None) -> None:
        self.repo = repo or db_repo

    def execute(self, plan: QueryPlan) -> ExecutionResult:
        """Validate safety, execute query, and measure latency."""
        # 1. Enforce SQL safety
        validate_sql_safety(plan.sql)

        # 2. Measure execution duration
        start_time = time.perf_counter()
        records = self.repo.query_dicts(plan.sql, plan.params)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return ExecutionResult(
            records=records,
            row_count=len(records),
            sql_duration_ms=round(duration_ms, 2),
            view_used=plan.base_view,
            is_empty=(len(records) == 0),
            plan=plan,
        )


executor = GovernedExecutor()
