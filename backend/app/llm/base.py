from __future__ import annotations

from typing import Protocol

from app.domain.schemas import DecisionBrief, TaskContract
from app.retrieval.hybrid import RetrievedChunk


class DecisionModelProvider(Protocol):
    name: str

    def compose_decision_brief(
        self,
        *,
        contract: TaskContract,
        evidence: list[RetrievedChunk],
        pricing: list[dict],
        profile: str,
    ) -> DecisionBrief:
        """Produce a structured decision brief with evidence-linked claims."""
