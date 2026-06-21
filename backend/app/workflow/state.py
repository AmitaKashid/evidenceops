from __future__ import annotations

from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    run_id: str
    tenant_id: str
    title: str
    user_request: str
    model_profile: str
    allowed_document_ids: list[str]
    require_human_review: bool
    contract: dict[str, Any]
    retrieved_evidence: list[dict[str, Any]]
    pricing_results: list[dict[str, Any]]
    research_results: list[dict[str, Any]]
    decision_brief: dict[str, Any]
    verification: dict[str, Any]
    quality_gaps: list[str]
    status: str
    stage_metrics: dict[str, int]
    error: str | None
