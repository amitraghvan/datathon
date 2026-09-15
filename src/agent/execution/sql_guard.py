"""SQL safety guard enforcing read-only execution and preventing SQL injection."""

import re
from typing import Set

DISALLOWED_KEYWORDS: Set[str] = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "REPLACE",
    "COPY",
    "ATTACH",
    "DETACH",
    "INSTALL",
    "LOAD",
    "EXPORT",
    "IMPORT",
    "PRAGMA",
    "EXEC",
    "EXECUTE",
    "CALL",
    "SYSTEM",
    "SH",
    "SHELL",
    "WRITE_PARQUET",
    "COPY_TO",
}

DISALLOWED_PATTERNS = [
    r";\s*\w+",  # Query chaining
    r"--",        # Line comments used in injection
    r"/\*.*?\*/", # Block comments
    r"\bread_csv\b",
    r"\bread_parquet\b",
    r"\bread_json\b",
    r"\bhttpfs\b",
]


class SecurityViolationError(Exception):
    """Raised when an unsafe or non-read-only SQL statement is intercepted."""
    pass


def validate_sql_safety(sql: str) -> bool:
    """Strictly validate that SQL is read-only and free of DDL/DML/injection attacks."""
    cleaned = sql.strip()

    # 1. Must start with SELECT or WITH
    if not (cleaned.upper().startswith("SELECT") or cleaned.upper().startswith("WITH")):
        raise SecurityViolationError("Only SELECT or WITH read-only queries are permitted.")

    # 2. Check forbidden keywords
    tokens = re.findall(r"\b[A-Za-z_]+\b", cleaned)
    for token in tokens:
        if token.upper() in DISALLOWED_KEYWORDS:
            raise SecurityViolationError(f"Security violation: Disallowed keyword '{token.upper()}' detected.")

    # 3. Check forbidden regex patterns
    for pattern in DISALLOWED_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            raise SecurityViolationError("Security violation: Malicious SQL pattern detected.")

    return True


class SQLGuard:
    """Class wrapper for SQL safety validation."""

    @staticmethod
    def validate(sql: str) -> bool:
        """Validate read-only safety."""
        return validate_sql_safety(sql)
