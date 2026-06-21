from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep, SettingsDep, TenantDep
from app.domain.enums import ModelProfileName
from app.domain.schemas import (
    EvaluationCase,
    EvaluationRunRequest,
    EvaluationRunResponse,
    ModelProfile,
)
from app.evaluation.runner import EvaluationRunner

router = APIRouter(prefix="/evaluations", tags=["evaluations"])

MODEL_PROFILES = [
    ModelProfile(
        name=ModelProfileName.ENTERPRISE_FAST,
        description="Optimized for classification, extraction, and lower-risk drafting with deterministic verification.",
        quality_bias=0.67,
        cost_index=0.4,
        latency_target_ms=1800,
        intended_use="High-volume routing, extraction, and low-complexity document tasks.",
    ),
    ModelProfile(
        name=ModelProfileName.ENTERPRISE_BALANCED,
        description="Default profile for evidence-grounded analysis with a balance of quality, latency, and cost.",
        quality_bias=0.82,
        cost_index=1.0,
        latency_target_ms=4200,
        intended_use="Cross-document decision briefs and normal power-user workflows.",
    ),
    ModelProfile(
        name=ModelProfileName.ENTERPRISE_PRECISE,
        description="Reserved for consequential reasoning, complex synthesis, and high-review workflows.",
        quality_bias=0.92,
        cost_index=2.4,
        latency_target_ms=8200,
        intended_use="Complex, high-value, or high-ambiguity tasks that justify a stricter quality budget.",
    ),
]


@router.get("/cases", response_model=list[EvaluationCase])
def list_cases(settings: SettingsDep) -> list[EvaluationCase]:
    return EvaluationRunner(settings).list_cases()


@router.get("/model-profiles", response_model=list[ModelProfile])
def list_model_profiles() -> list[ModelProfile]:
    return MODEL_PROFILES


@router.post("/runs", response_model=EvaluationRunResponse, status_code=status.HTTP_201_CREATED)
def run_evaluation(
    payload: EvaluationRunRequest,
    session: SessionDep,
    settings: SettingsDep,
    tenant_id: TenantDep,
) -> EvaluationRunResponse:
    payload.tenant_id = tenant_id
    try:
        return EvaluationRunner(settings).run(session, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
