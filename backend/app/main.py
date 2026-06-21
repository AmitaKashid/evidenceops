from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import EvidenceOpsError
from app.core.logging import configure_logging
from app.db.session import SessionLocal, initialize_database
from app.retrieval.store import KnowledgeStore

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings.log_level)
    initialize_database()
    with SessionLocal() as session:
        KnowledgeStore().seed_demo_documents(session, settings.default_tenant_id)
    logger.info("EvidenceOps API started", extra={"environment": settings.environment})
    yield
    logger.info("EvidenceOps API stopped")


app = FastAPI(
    title="EvidenceOps API",
    version="0.1.0",
    description="Governed decision-brief agent and evaluation control plane.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Tenant-ID"],
)


@app.exception_handler(EvidenceOpsError)
async def domain_error_handler(_: Request, exc: EvidenceOpsError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled API error", extra={"error": str(exc)})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
def root_health() -> dict[str, str]:
    return {"status": "ok", "service": "evidenceops-api"}
