from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums import (
    FindingSeverity,
    ModelProfileName,
    ReviewDecision,
    RunStatus,
    VerificationSeverity,
)


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class SourceReference(APIModel):
    document_id: str
    chunk_id: str
    title: str
    section: str
    excerpt: str = Field(min_length=1, max_length=1200)
    score: float = Field(ge=0.0, le=1.0)
    source_type: Literal["internal", "pricing", "public_research"] = "internal"


class TaskRequest(APIModel):
    title: str = Field(min_length=6, max_length=160)
    request: str = Field(min_length=25, max_length=6000)
    model_profile: ModelProfileName = ModelProfileName.ENTERPRISE_BALANCED
    tenant_id: str | None = Field(default=None, min_length=3, max_length=80)
    source_document_ids: list[str] = Field(default_factory=list, max_length=40)
    require_human_review: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("request")
    @classmethod
    def reject_external_actions(cls, value: str) -> str:
        forbidden = ("send email", "execute payment", "delete record", "sign contract")
        lowered = value.lower()
        if any(phrase in lowered for phrase in forbidden):
            raise ValueError(
                "This reference workflow is read-only. Request analysis and a draft, then approve external actions separately."
            )
        return value


class TaskContract(APIModel):
    objective: str
    deliverable: str
    required_capabilities: list[str]
    allowed_source_types: list[str]
    approval_required: bool
    escalation_conditions: list[str]
    quality_bar: list[str]
    constraints: list[str]


class StructuredFinding(APIModel):
    finding_id: str
    category: Literal["security", "cost", "policy", "capability", "risk", "research"]
    title: str
    statement: str
    severity: FindingSeverity
    evidence: list[SourceReference] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    requires_review: bool = False


class DecisionClaim(APIModel):
    claim_id: str
    statement: str
    importance: Literal["material", "supporting"]
    citations: list[SourceReference] = Field(min_length=1)
    numeric_values: dict[str, float] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)


class DecisionBrief(APIModel):
    executive_summary: str
    recommendation: str
    rationale: list[str] = Field(min_length=1)
    tradeoffs: list[str] = Field(default_factory=list)
    findings: list[StructuredFinding] = Field(default_factory=list)
    claims: list[DecisionClaim] = Field(min_length=1)
    assumptions: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    generated_by: str


class VerificationIssue(APIModel):
    rule_id: str
    severity: VerificationSeverity
    message: str
    claim_id: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    remediation: str | None = None


class VerificationResult(APIModel):
    passed: bool
    quality_score: float = Field(ge=0.0, le=1.0)
    citation_coverage: float = Field(ge=0.0, le=1.0)
    citation_precision: float = Field(ge=0.0, le=1.0)
    numeric_accuracy: float = Field(ge=0.0, le=1.0)
    escalation_required: bool
    issues: list[VerificationIssue] = Field(default_factory=list)


class RunEventResponse(APIModel):
    sequence: int
    event_type: str
    stage: str
    payload: dict[str, Any]
    created_at: datetime


class ReviewRequest(APIModel):
    decision: ReviewDecision
    reviewer: str = Field(min_length=2, max_length=120)
    comment: str = Field(default="", max_length=2000)


class ReviewRecord(APIModel):
    decision: ReviewDecision
    reviewer: str
    comment: str
    reviewed_at: datetime


class TaskRunResponse(APIModel):
    id: UUID
    tenant_id: str
    title: str
    request: str
    model_profile: ModelProfileName
    status: RunStatus
    created_at: datetime
    updated_at: datetime
    decision_brief: DecisionBrief | None = None
    verification: VerificationResult | None = None
    review: ReviewRecord | None = None
    events: list[RunEventResponse] = Field(default_factory=list)


class TaskRunListResponse(APIModel):
    items: list[TaskRunResponse]
    total: int


class KnowledgeDocumentRequest(APIModel):
    document_id: str = Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_.-]+$")
    title: str = Field(min_length=3, max_length=250)
    source_type: Literal["internal", "pricing", "public_research"] = "internal"
    content: str = Field(min_length=40, max_length=30000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeDocumentResponse(APIModel):
    document_id: str
    title: str
    source_type: str
    content_hash: str
    created_at: datetime


class ModelProfile(APIModel):
    name: ModelProfileName
    description: str
    quality_bias: float = Field(ge=0.0, le=1.0)
    cost_index: float = Field(ge=0.0)
    latency_target_ms: int = Field(ge=1)
    intended_use: str


class EvaluationCase(APIModel):
    task_id: str
    title: str
    prompt: str
    expected_vendor: str | None = None
    expected_claim_fragments: list[str] = Field(default_factory=list)
    expected_document_ids: list[str] = Field(default_factory=list)
    expected_escalation: bool = False
    tags: list[str] = Field(default_factory=list)


class EvaluationRunRequest(APIModel):
    model_profiles: list[ModelProfileName] = Field(
        default_factory=lambda: [
            ModelProfileName.ENTERPRISE_FAST,
            ModelProfileName.ENTERPRISE_BALANCED,
            ModelProfileName.ENTERPRISE_PRECISE,
        ],
        min_length=1,
        max_length=3,
    )
    task_ids: list[str] = Field(default_factory=list, max_length=100)
    tenant_id: str | None = None


class EvaluationResultResponse(APIModel):
    task_id: str
    model_profile: ModelProfileName
    task_completion: float
    citation_coverage: float
    numeric_accuracy: float
    escalation_correctness: float
    latency_ms: int
    estimated_cost_usd: float
    composite_score: float
    notes: list[str] = Field(default_factory=list)


class EvaluationRunResponse(APIModel):
    id: UUID
    tenant_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    configuration: dict[str, Any]
    summary: dict[str, Any]
    results: list[EvaluationResultResponse]


class DashboardSummary(APIModel):
    total_runs: int
    waiting_for_review: int
    approval_rate: float
    average_quality_score: float
    average_latency_ms: int
    open_verification_issues: int
    latest_evaluation_summary: dict[str, Any] | None = None
    recent_runs: list[TaskRunResponse] = Field(default_factory=list)
