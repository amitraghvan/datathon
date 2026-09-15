"""Main FastAPI application factory for EduPulse AI Enterprise Platform."""

import logging
import time

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.v1 import (
    agent,
    districts,
    insights,
    overview,
    procurement,
    quality,
    risk,
    schools,
    welfare,
)
from backend.app.config import settings
from backend.app.repository.duckdb import db_repo
from backend.app.utils.errors import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("edupulse.api")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Explicit CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Log incoming API requests with duration and status code."""
    start_time = time.time()
    try:
        response = await call_next(request)
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration}ms)")
        return response
    except Exception as exc:
        duration = round((time.time() - start_time) * 1000, 2)
        logger.error(f"{request.method} {request.url.path} FAILED after {duration}ms: {exc}")
        raise exc


# Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include v1 Routers using APIRouter for unified exception propagation
api_v1 = APIRouter(prefix=settings.API_V1_STR)
api_v1.include_router(overview.router, tags=["Overview"])
api_v1.include_router(districts.router, prefix="/districts", tags=["Districts"])
api_v1.include_router(schools.router, prefix="/schools", tags=["Schools"])
api_v1.include_router(welfare.router, prefix="/welfare", tags=["Welfare & Infrastructure"])
api_v1.include_router(procurement.router, prefix="/procurement", tags=["Procurement"])
api_v1.include_router(risk.router, prefix="/risk", tags=["Risk & Intervention"])
api_v1.include_router(quality.router, prefix="/quality", tags=["Data Trust & Governance"])
api_v1.include_router(insights.router, prefix="/insights", tags=["Advanced Insights"])
api_v1.include_router(agent.router, prefix="/agent", tags=["AI Analyst (Phase 6 Preview)"])

app.include_router(api_v1)


@app.get("/", summary="Root status")
def root_status() -> JSONResponse:
    """Root entrypoint reporting service and API documentation links."""
    return JSONResponse(
        content={
            "product": "EduPulse AI",
            "subtitle": "Education Welfare Command Center",
            "tagline": "Clean. Connect. Detect. Explain. Act.",
            "version": settings.VERSION,
            "docs": "/docs",
            "api_base": settings.API_V1_STR,
            "data_trust_score": 94.6,
        }
    )


@app.get("/health", summary="Health check")
def health_check():
    """Top-level health check endpoint."""
    return overview.get_health(db_repo)
