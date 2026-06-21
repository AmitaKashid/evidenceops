from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import SessionDep, SettingsDep, TenantDep
from app.core.errors import NotFoundError
from app.domain.schemas import (
    KnowledgeDocumentRequest,
    KnowledgeDocumentResponse,
    ReviewRequest,
    TaskRequest,
    TaskRunListResponse,
    TaskRunResponse,
)
from app.retrieval.store import KnowledgeStore
from app.services.task_service import TaskOrchestrator

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/runs", response_model=TaskRunResponse, status_code=status.HTTP_201_CREATED)
def create_task_run(
    payload: TaskRequest,
    session: SessionDep,
    settings: SettingsDep,
    tenant_id: TenantDep,
) -> TaskRunResponse:
    payload.tenant_id = tenant_id
    try:
        return TaskOrchestrator(settings).execute(session, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/runs", response_model=TaskRunListResponse)
def list_task_runs(
    session: SessionDep,
    settings: SettingsDep,
    tenant_id: TenantDep,
    limit: int = Query(default=30, ge=1, le=100),
) -> TaskRunListResponse:
    items = TaskOrchestrator(settings).list(session, tenant_id=tenant_id, limit=limit)
    return TaskRunListResponse(items=items, total=len(items))


@router.get("/runs/{run_id}", response_model=TaskRunResponse)
def get_task_run(
    run_id: str,
    session: SessionDep,
    settings: SettingsDep,
    tenant_id: TenantDep,
) -> TaskRunResponse:
    try:
        return TaskOrchestrator(settings).get(session, tenant_id=tenant_id, run_id=run_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/runs/{run_id}/review", response_model=TaskRunResponse)
def record_review(
    run_id: str,
    payload: ReviewRequest,
    session: SessionDep,
    settings: SettingsDep,
    tenant_id: TenantDep,
) -> TaskRunResponse:
    try:
        return TaskOrchestrator(settings).review(
            session,
            tenant_id=tenant_id,
            run_id=run_id,
            review_request=payload,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/knowledge/documents", response_model=KnowledgeDocumentResponse, status_code=status.HTTP_201_CREATED)
def upsert_knowledge_document(
    payload: KnowledgeDocumentRequest,
    session: SessionDep,
    tenant_id: TenantDep,
) -> KnowledgeDocumentResponse:
    return KnowledgeStore().upsert(session, tenant_id, payload)
