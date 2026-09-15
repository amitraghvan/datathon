"""Structured error handling and enterprise exception types."""

from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class SchoolNotFoundException(AppException):
    """Raised when a school identifier cannot be located."""

    def __init__(self, school_id: str) -> None:
        super().__init__(
            code="SCHOOL_NOT_FOUND",
            message=f"School '{school_id}' was not found in canonical master records.",
            status_code=404,
            details={"school_id": school_id},
        )


class DistrictNotFoundException(AppException):
    """Raised when a district identifier cannot be located."""

    def __init__(self, district: str) -> None:
        super().__init__(
            code="DISTRICT_NOT_FOUND",
            message=f"District '{district}' was not found in canonical master records.",
            status_code=404,
            details={"district": district},
        )


class InvalidFilterException(AppException):
    """Raised when an impossible or invalid filter combination is supplied."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="INVALID_FILTER_PARAMETERS",
            message=message,
            status_code=422,
            details=details,
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Structured handler for business and operational exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Safe fallback handler preventing stack trace leakage."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while executing analytical query.",
                "details": {"exception_type": type(exc).__name__},
            }
        },
    )
