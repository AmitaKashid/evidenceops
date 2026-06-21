from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TaskRunModel(Base):
    __tablename__ = "task_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    request: Mapped[str] = mapped_column(Text, nullable=False)
    model_profile: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(48), index=True, nullable=False)
    contract_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    state_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    decision_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    verification_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    review_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    events: Mapped[list["TaskEventModel"]] = relationship(
        back_populates="run", cascade="all, delete-orphan", order_by="TaskEventModel.sequence"
    )


class TaskEventModel(Base):
    __tablename__ = "task_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("task_runs.id", ondelete="CASCADE"), index=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    run: Mapped[TaskRunModel] = relationship(back_populates="events")


class KnowledgeDocumentModel(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    document_id: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class EvaluationRunModel(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    configuration_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    summary_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    results: Mapped[list["EvaluationResultModel"]] = relationship(
        back_populates="evaluation_run", cascade="all, delete-orphan"
    )


class EvaluationResultModel(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evaluation_run_id: Mapped[str] = mapped_column(
        ForeignKey("evaluation_runs.id", ondelete="CASCADE"), index=True
    )
    task_id: Mapped[str] = mapped_column(String(120), nullable=False)
    model_profile: Mapped[str] = mapped_column(String(64), nullable=False)
    task_completion: Mapped[float] = mapped_column(Float, nullable=False)
    citation_coverage: Mapped[float] = mapped_column(Float, nullable=False)
    numeric_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    escalation_correctness: Mapped[float] = mapped_column(Float, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False)
    notes_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    evaluation_run: Mapped[EvaluationRunModel] = relationship(back_populates="results")
