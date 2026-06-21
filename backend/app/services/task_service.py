from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import TaskRunModel
from app.domain.enums import EventType, ModelProfileName, ReviewDecision, RunStatus
from app.domain.schemas import (
    DecisionBrief,
    ReviewRecord,
    ReviewRequest,
    RunEventResponse,
    TaskRequest,
    TaskRunResponse,
    VerificationResult,
)
from app.llm.providers import build_provider
from app.observability.tracing import WorkflowTracer
from app.repositories.runs import TaskRunRepository
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.store import KnowledgeStore
from app.tools.spreadsheet import PricingAnalysisTool
from app.tools.web_research import GuardedResearchTool
from app.workflow.graph import build_workflow_graph
from app.workflow.nodes import WorkflowNodes
from app.workflow.state import WorkflowState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WorkflowExecution:
    state: WorkflowState
    elapsed_ms: int


class WorkflowExecutor:
    """Constructs a graph per tenant so retrieval scope is explicit and isolated."""

    def __init__(self, settings: Settings, session: Session, tenant_id: str) -> None:
        knowledge_store = KnowledgeStore()
        documents = knowledge_store.list_for_tenant(session, tenant_id)
        if not documents:
            raise ValueError("No knowledge documents exist for the active tenant.")
        retriever = HybridRetriever(documents)
        pricing_file = settings.data_root / "demo" / "vendor_pricing.csv"
        self.nodes = WorkflowNodes(
            settings=settings,
            retriever=retriever,
            provider=build_provider(settings),
            pricing_tool=PricingAnalysisTool(pricing_file),
            research_tool=GuardedResearchTool(),
        )
        self.graph = build_workflow_graph(self.nodes)
        self.tracer = WorkflowTracer(settings)

    def execute(self, initial_state: WorkflowState, stage_callback=None) -> WorkflowExecution:
        current_state: WorkflowState = initial_state.copy()
        started = time.perf_counter()
        trace_attributes = {
            "evidenceops.run_id": initial_state["run_id"],
            "evidenceops.tenant_id": initial_state["tenant_id"],
            "gen_ai.request.model": initial_state["model_profile"],
        }
        try:
            with self.tracer.stage("evidenceops.workflow.execute", trace_attributes) as trace_result:
                stream = iter(self.graph.stream(current_state, stream_mode="updates"))
                while True:
                    stage_started = time.perf_counter()
                    try:
                        update = next(stream)
                    except StopIteration:
                        break
                    latency_ms = int((time.perf_counter() - stage_started) * 1000)
                    for stage_name, stage_update in update.items():
                        if isinstance(stage_update, dict):
                            current_state.update(cast(WorkflowState, stage_update))
                        metrics = dict(current_state.get("stage_metrics", {}))
                        metrics[stage_name] = max(metrics.get(stage_name, 0), latency_ms)
                        current_state["stage_metrics"] = metrics
                        if stage_callback:
                            stage_callback(stage_name, stage_update if isinstance(stage_update, dict) else {}, latency_ms)
                trace_result["status"] = current_state.get("status", "unknown")
        except Exception as exc:
            current_state["status"] = RunStatus.FAILED.value
            current_state["error"] = str(exc)
            raise
        return WorkflowExecution(
            state=current_state,
            elapsed_ms=int((time.perf_counter() - started) * 1000),
        )


class TaskOrchestrator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.runs = TaskRunRepository()
        self.knowledge = KnowledgeStore()

    def execute(self, session: Session, request: TaskRequest) -> TaskRunResponse:
        tenant_id = request.tenant_id or self.settings.default_tenant_id
        self.knowledge.seed_demo_documents(session, tenant_id)
        run = self.runs.create(
            session,
            tenant_id=tenant_id,
            title=request.title,
            request=request.request,
            model_profile=request.model_profile.value,
        )
        run.status = RunStatus.RUNNING.value
        session.commit()
        session.refresh(run)

        initial: WorkflowState = {
            "run_id": run.id,
            "tenant_id": tenant_id,
            "title": request.title,
            "user_request": request.request,
            "model_profile": request.model_profile.value,
            "allowed_document_ids": request.source_document_ids,
            "require_human_review": request.require_human_review,
            "status": RunStatus.RUNNING.value,
            "stage_metrics": {},
        }

        def on_stage(stage: str, update: dict[str, Any], latency_ms: int) -> None:
            self.runs.append_event(
                session,
                run=run,
                event_type=EventType.STAGE_COMPLETED.value,
                stage=stage,
                payload={"latency_ms": latency_ms, "output_fields": sorted(update.keys())},
            )
            if stage == "verify_brief":
                verification = update.get("verification", {})
                self.runs.append_event(
                    session,
                    run=run,
                    event_type=EventType.VERIFICATION_COMPLETED.value,
                    stage=stage,
                    payload={
                        "quality_score": verification.get("quality_score"),
                        "passed": verification.get("passed"),
                        "issue_count": len(verification.get("issues", [])),
                    },
                )
            session.commit()

        try:
            executor = WorkflowExecutor(self.settings, session, tenant_id)
            execution = executor.execute(initial, stage_callback=on_stage)
            state = execution.state
            final_status = RunStatus(state.get("status", RunStatus.WAITING_FOR_REVIEW.value))
            self.runs.update_state(
                session,
                run=run,
                status=final_status,
                contract=state.get("contract", {}),
                state={
                    "retrieved_evidence": state.get("retrieved_evidence", []),
                    "pricing_results": state.get("pricing_results", []),
                    "research_results": state.get("research_results", []),
                    "stage_metrics": state.get("stage_metrics", {}),
                    "elapsed_ms": execution.elapsed_ms,
                },
                decision=state.get("decision_brief", {}),
                verification=state.get("verification", {}),
            )
            if final_status == RunStatus.WAITING_FOR_REVIEW:
                self.runs.append_event(
                    session,
                    run=run,
                    event_type=EventType.REVIEW_REQUESTED.value,
                    stage="human_review",
                    payload={"reason": "Workflow requires explicit reviewer decision before downstream use."},
                )
                session.commit()
        except Exception as exc:
            logger.exception("Task workflow failed", extra={"run_id": run.id})
            self.runs.append_event(
                session,
                run=run,
                event_type=EventType.STAGE_FAILED.value,
                stage="workflow",
                payload={"error": str(exc)},
            )
            self.runs.update_state(
                session,
                run=run,
                status=RunStatus.FAILED,
                state={"error": str(exc)},
            )
        return self.get(session, tenant_id=tenant_id, run_id=run.id)

    def get(self, session: Session, *, tenant_id: str, run_id: str) -> TaskRunResponse:
        record = self.runs.get(session, tenant_id=tenant_id, run_id=run_id)
        return self._to_response(record)

    def list(self, session: Session, *, tenant_id: str, limit: int = 30) -> list[TaskRunResponse]:
        return [self._to_response(item) for item in self.runs.list(session, tenant_id=tenant_id, limit=limit)]

    def review(
        self,
        session: Session,
        *,
        tenant_id: str,
        run_id: str,
        review_request: ReviewRequest,
    ) -> TaskRunResponse:
        record = self.runs.get(session, tenant_id=tenant_id, run_id=run_id)
        if record.status not in {RunStatus.WAITING_FOR_REVIEW.value, RunStatus.REJECTED.value}:
            raise ValueError(f"Run {run_id} is not eligible for review in status {record.status}.")
        now = datetime.now(timezone.utc)
        review = ReviewRecord(
            decision=review_request.decision,
            reviewer=review_request.reviewer,
            comment=review_request.comment,
            reviewed_at=now,
        )
        if review_request.decision == ReviewDecision.APPROVE:
            status = RunStatus.APPROVED
        elif review_request.decision == ReviewDecision.REJECT:
            status = RunStatus.REJECTED
        else:
            status = RunStatus.WAITING_FOR_REVIEW
        record.review_json = review.model_dump(mode="json")
        self.runs.append_event(
            session,
            run=record,
            event_type=EventType.REVIEW_RECORDED.value,
            stage="human_review",
            payload=review.model_dump(mode="json"),
        )
        self.runs.update_state(session, run=record, status=status)
        return self.get(session, tenant_id=tenant_id, run_id=run_id)

    @staticmethod
    def _to_response(record: TaskRunModel) -> TaskRunResponse:
        decision = DecisionBrief.model_validate(record.decision_json) if record.decision_json else None
        verification = VerificationResult.model_validate(record.verification_json) if record.verification_json else None
        review = ReviewRecord.model_validate(record.review_json) if record.review_json else None
        events = [
            RunEventResponse(
                sequence=item.sequence,
                event_type=item.event_type,
                stage=item.stage,
                payload=item.payload_json,
                created_at=item.created_at,
            )
            for item in record.events
        ]
        return TaskRunResponse(
            id=UUID(record.id),
            tenant_id=record.tenant_id,
            title=record.title,
            request=record.request,
            model_profile=ModelProfileName(record.model_profile),
            status=RunStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            decision_brief=decision,
            verification=verification,
            review=review,
            events=events,
        )
