"""DuckDB connection and execution engine."""

import logging
from typing import Any, Dict, List, Optional

import duckdb
import pandas as pd

from backend.app.config import settings

logger = logging.getLogger("edupulse.repository")


class DuckDBRepository:
    """Manages read-only connection to canonical DuckDB warehouse."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = str(db_path or settings.DUCKDB_PATH)

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Create a read-only DuckDB connection."""
        return duckdb.connect(self.db_path, read_only=True)

    def query_df(self, sql: str, params: Optional[List[Any]] = None) -> pd.DataFrame:
        """Execute query and return pandas DataFrame."""
        with self.get_connection() as con:
            if params:
                return con.execute(sql, params).df()
            return con.execute(sql).df()

    def query_dicts(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Execute query and return list of dictionaries."""
        df = self.query_df(sql, params)
        # Convert NaN and NaT to None for clean JSON serialization
        return df.where(pd.notnull(df), None).to_dict(orient="records")

    def query_one(self, sql: str, params: Optional[List[Any]] = None) -> Optional[Dict[str, Any]]:
        """Execute query and return a single row dictionary or None."""
        records = self.query_dicts(sql, params)
        return records[0] if records else None


# Singleton instance
db_repo = DuckDBRepository()
