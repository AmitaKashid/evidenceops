from __future__ import annotations

import statistics

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import SessionDep, SettingsDep, TenantDep
from app.db.models import EvaluationRunModel, TaskRunModel
from app.domain.enums import RunStatus
from app.domain.schemas import DashboardSummary
from app.services.task_service import TaskOrchestrator

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    session: SessionDep,
    settings: SettingsDep,
    tenant_id: TenantDep,
) -> DashboardSummary:
    total_runs = session.scalar(
        select(func.count(TaskRunModel.id)).where(TaskRunModel.tenant_id == tenant_id)
    ) or 0
    waiting_for_review = session.scalar(
        select(func.count(TaskRunModel.id)).where(
            TaskRunModel.tenant_id == tenant_id,
            TaskRunModel.status == RunStatus.WAITING_FOR_REVIEW.value,
        )
    ) or 0
    approved = session.scalar(
        select(func.count(TaskRunModel.id)).where(
            TaskRunModel.tenant_id == tenant_id,
            TaskRunModel.status == RunStatus.APPROVED.value,
        )
    ) or 0
    completed_or_reviewed = max(
        session.scalar(
            select(func.count(TaskRunModel.id)).where(
                TaskRunModel.tenant_id == tenant_id,
                TaskRunModel.status.in_([
                    RunStatus.APPROVED.value,
                    RunStatus.REJECTED.value,
                    RunStatus.WAITING_FOR_REVIEW.value,
                ]),
            )
        ) or 0,
        1,
    )
    recent = TaskOrchestrator(settings).list(session, tenant_id=tenant_id, limit=8)
    quality_scores = [
        run.verification.quality_score
        for run in recent
        if run.verification is not None
    ]
    latency_values = [
        int(run.events[-1].payload.get("latency_ms", 0))
        for run in recent
        if run.events and isinstance(run.events[-1].payload, dict)
    ]
    issue_count = sum(
        len(run.verification.issues)
        for run in recent
        if run.verification is not None
    )
    latest_evaluation = session.scalar(
        select(EvaluationRunModel)
        .where(EvaluationRunModel.tenant_id == tenant_id, EvaluationRunModel.status == "completed")
        .order_by(EvaluationRunModel.completed_at.desc())
    )
    return DashboardSummary(
        total_runs=total_runs,
        waiting_for_review=waiting_for_review,
        approval_rate=round(approved / completed_or_reviewed, 3),
        average_quality_score=round(statistics.fmean(quality_scores), 3) if quality_scores else 0.0,
        average_latency_ms=round(statistics.fmean(latency_values)) if latency_values else 0,
        open_verification_issues=issue_count,
        latest_evaluation_summary=latest_evaluation.summary_json if latest_evaluation else None,
        recent_runs=recent,
    )
