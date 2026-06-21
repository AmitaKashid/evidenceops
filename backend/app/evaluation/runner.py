from __future__ import annotations

import statistics
import time
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import EvaluationResultModel, EvaluationRunModel
from app.domain.enums import ModelProfileName
from app.domain.schemas import (
    DecisionBrief,
    EvaluationCase,
    EvaluationResultResponse,
    EvaluationRunRequest,
    EvaluationRunResponse,
    VerificationResult,
)
from app.evaluation.scorers import EvaluationScorer
from app.evaluation.taskbench import TaskBenchRepository
from app.services.task_service import WorkflowExecutor
from app.workflow.state import WorkflowState

PROFILE_COSTS = {
    ModelProfileName.ENTERPRISE_FAST.value: 0.004,
    ModelProfileName.ENTERPRISE_BALANCED.value: 0.010,
    ModelProfileName.ENTERPRISE_PRECISE.value: 0.024,
}


class EvaluationRunner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.taskbench = TaskBenchRepository(settings.data_root / "taskbench" / "cases.json")
        self.scorer = EvaluationScorer()

    def list_cases(self) -> list[EvaluationCase]:
        return self.taskbench.list_cases()

    def run(self, session: Session, request: EvaluationRunRequest) -> EvaluationRunResponse:
        tenant_id = request.tenant_id or self.settings.default_tenant_id
        cases = self.taskbench.select(request.task_ids)
        run = EvaluationRunModel(
            tenant_id=tenant_id,
            status="running",
            configuration_json={
                "model_profiles": [profile.value for profile in request.model_profiles],
                "task_ids": [case.task_id for case in cases],
                "taskbench_version": "2026.06.demo.v1",
            },
        )
        session.add(run)
        session.commit()
        session.refresh(run)

        results: list[EvaluationResultResponse] = []
        for profile in request.model_profiles:
            executor = WorkflowExecutor(self.settings, session, tenant_id)
            for case in cases:
                initial: WorkflowState = {
                    "run_id": f"evaluation::{run.id}::{case.task_id}",
                    "tenant_id": tenant_id,
                    "title": case.title,
                    "user_request": case.prompt,
                    "model_profile": profile.value,
                    "allowed_document_ids": [],
                    "require_human_review": True,
                    "status": "running",
                    "stage_metrics": {},
                }
                started = time.perf_counter()
                execution = executor.execute(initial)
                latency_ms = max(int((time.perf_counter() - started) * 1000), 1)
                brief = DecisionBrief.model_validate(execution.state["decision_brief"])
                verification = VerificationResult.model_validate(execution.state["verification"])
                score = self.scorer.score(case=case, brief=brief, verification=verification)
                response = EvaluationResultResponse(
                    task_id=case.task_id,
                    model_profile=profile,
                    task_completion=score.task_completion,
                    citation_coverage=score.citation_coverage,
                    numeric_accuracy=score.numeric_accuracy,
                    escalation_correctness=score.escalation_correctness,
                    latency_ms=latency_ms,
                    estimated_cost_usd=PROFILE_COSTS[profile.value],
                    composite_score=score.composite_score,
                    notes=score.notes,
                )
                results.append(response)
                session.add(
                    EvaluationResultModel(
                        evaluation_run_id=run.id,
                        task_id=response.task_id,
                        model_profile=response.model_profile.value,
                        task_completion=response.task_completion,
                        citation_coverage=response.citation_coverage,
                        numeric_accuracy=response.numeric_accuracy,
                        escalation_correctness=response.escalation_correctness,
                        latency_ms=response.latency_ms,
                        estimated_cost_usd=response.estimated_cost_usd,
                        composite_score=response.composite_score,
                        notes_json=response.notes,
                    )
                )
        summary = self._summarize(results)
        run.status = "completed"
        run.summary_json = summary
        run.completed_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(run)
        return self._to_response(run, results)

    @staticmethod
    def _summarize(results: list[EvaluationResultResponse]) -> dict[str, Any]:
        if not results:
            return {"total_cases": 0, "profiles": {}}
        grouped: dict[str, list[EvaluationResultResponse]] = {}
        for result in results:
            grouped.setdefault(result.model_profile.value, []).append(result)
        profiles: dict[str, dict[str, float]] = {}
        for profile, values in grouped.items():
            profiles[profile] = {
                "composite_score": round(statistics.fmean(item.composite_score for item in values), 3),
                "task_completion": round(statistics.fmean(item.task_completion for item in values), 3),
                "citation_coverage": round(statistics.fmean(item.citation_coverage for item in values), 3),
                "numeric_accuracy": round(statistics.fmean(item.numeric_accuracy for item in values), 3),
                "latency_ms": round(statistics.fmean(item.latency_ms for item in values), 1),
                "estimated_cost_usd": round(sum(item.estimated_cost_usd for item in values), 4),
            }
        highest_score = max(profile["composite_score"] for profile in profiles.values())
        winners = [
            name
            for name, profile in profiles.items()
            if abs(profile["composite_score"] - highest_score) < 0.001
        ]
        return {
            "total_cases": len(results),
            "profiles": profiles,
            "best_profile": winners[0] if len(winners) == 1 else None,
            "comparison_mode": (
                "comparative" if len(winners) == 1 else "tie: local deterministic provider validates control-plane plumbing"
            ),
        }

    @staticmethod
    def _to_response(run: EvaluationRunModel, results: list[EvaluationResultResponse]) -> EvaluationRunResponse:
        return EvaluationRunResponse(
            id=UUID(run.id),
            tenant_id=run.tenant_id,
            status=run.status,
            started_at=run.started_at,
            completed_at=run.completed_at,
            configuration=run.configuration_json,
            summary=run.summary_json,
            results=results,
        )
