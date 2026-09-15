"""DuckDB analytical database connectivity and execution engine."""

from pathlib import Path
from typing import Optional

import duckdb
import pandas as pd

from src.config import DUCKDB_PATH, logger


def get_db_connection(
    db_path: Optional[Path] = None, read_only: bool = False
) -> duckdb.DuckDBPyConnection:
    """Acquire DuckDB database connection.

    Args:
        db_path: Optional target file path (defaults to config.DUCKDB_PATH).
        read_only: Open in read-only mode for dashboard queries.
    """
    target = db_path or DUCKDB_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(target), read_only=read_only)
    return con


def execute_sql_file(con: duckdb.DuckDBPyConnection, sql_path: Path) -> None:
    """Execute multi-statement SQL script file."""
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found at {sql_path}")
    logger.info("Executing SQL file: %s", sql_path)
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()
    con.execute(sql_content)
    logger.info("Executed SQL file successfully: %s", sql_path.name)


def query_to_df(query: str, con: Optional[duckdb.DuckDBPyConnection] = None) -> pd.DataFrame:
    """Execute SQL query and return pandas DataFrame."""
    should_close = False
    if con is None:
        con = get_db_connection(read_only=True)
        should_close = True
    try:
        df = con.execute(query).df()
        return df
    finally:
        if should_close:
            con.close()
