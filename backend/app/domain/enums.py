from __future__ import annotations

from enum import StrEnum


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_FOR_REVIEW = "waiting_for_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


class ReviewDecision(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"


class EventType(StrEnum):
    RUN_CREATED = "run.created"
    STAGE_STARTED = "stage.started"
    STAGE_COMPLETED = "stage.completed"
    STAGE_FAILED = "stage.failed"
    TOOL_CALLED = "tool.called"
    VERIFICATION_COMPLETED = "verification.completed"
    REVIEW_REQUESTED = "review.requested"
    REVIEW_RECORDED = "review.recorded"
    EVALUATION_COMPLETED = "evaluation.completed"


class FindingSeverity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class VerificationSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ModelProfileName(StrEnum):
    ENTERPRISE_FAST = "enterprise-fast"
    ENTERPRISE_BALANCED = "enterprise-balanced"
    ENTERPRISE_PRECISE = "enterprise-precise"
