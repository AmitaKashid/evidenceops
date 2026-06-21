from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import NotFoundError
from app.core.security import redact_payload
from app.db.models import TaskEventModel, TaskRunModel
from app.domain.enums import EventType, RunStatus


class TaskRunRepository:
    def create(
        self,
        session: Session,
        *,
        tenant_id: str,
        title: str,
        request: str,
        model_profile: str,
    ) -> TaskRunModel:
        record = TaskRunModel(
            tenant_id=tenant_id,
            title=title,
            request=request,
            model_profile=model_profile,
            status=RunStatus.QUEUED.value,
        )
        session.add(record)
        session.flush()
        self.append_event(
            session,
            run=record,
            event_type=EventType.RUN_CREATED.value,
            stage="intake",
            payload={"title": title, "model_profile": model_profile},
        )
        session.commit()
        session.refresh(record)
        return record

    def append_event(
        self,
        session: Session,
        *,
        run: TaskRunModel,
        event_type: str,
        stage: str,
        payload: dict[str, Any],
    ) -> TaskEventModel:
        sequence = (
            session.scalar(select(func.max(TaskEventModel.sequence)).where(TaskEventModel.run_id == run.id)) or 0
        ) + 1
        event = TaskEventModel(
            run_id=run.id,
            sequence=sequence,
            event_type=event_type,
            stage=stage,
            payload_json=redact_payload(payload),
        )
        session.add(event)
        return event

    def get(self, session: Session, *, tenant_id: str, run_id: str) -> TaskRunModel:
        statement = (
            select(TaskRunModel)
            .options(selectinload(TaskRunModel.events))
            .where(TaskRunModel.id == run_id, TaskRunModel.tenant_id == tenant_id)
        )
        record = session.scalar(statement)
        if record is None:
            raise NotFoundError("Task run was not found for the active tenant.")
        return record

    def list(self, session: Session, *, tenant_id: str, limit: int = 30) -> list[TaskRunModel]:
        statement = (
            select(TaskRunModel)
            .options(selectinload(TaskRunModel.events))
            .where(TaskRunModel.tenant_id == tenant_id)
            .order_by(TaskRunModel.created_at.desc())
            .limit(limit)
        )
        return list(session.scalars(statement).unique().all())

    def update_state(
        self,
        session: Session,
        *,
        run: TaskRunModel,
        status: RunStatus,
        contract: dict[str, Any] | None = None,
        state: dict[str, Any] | None = None,
        decision: dict[str, Any] | None = None,
        verification: dict[str, Any] | None = None,
    ) -> TaskRunModel:
        run.status = status.value
        if contract is not None:
            run.contract_json = contract
        if state is not None:
            run.state_json = redact_payload(state)
        if decision is not None:
            run.decision_json = decision
        if verification is not None:
            run.verification_json = verification
        run.updated_at = datetime.now(timezone.utc)
        session.add(run)
        session.commit()
        session.refresh(run)
        return run
