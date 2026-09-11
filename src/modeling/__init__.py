"""Canonical dimensional modeling and DuckDB data mart package."""

from .build_database import build_canonical_database
from .database import execute_sql_file, get_db_connection

__all__ = [
    "get_db_connection",
    "execute_sql_file",
    "build_canonical_database",
]
