from __future__ import annotations

from app.domain.schemas import DecisionBrief


class BriefQualityRules:
    """Small deterministic quality gate for output completeness."""

    def assess(self, brief: DecisionBrief) -> list[str]:
        gaps: list[str] = []
        if len(brief.executive_summary.split()) < 18:
            gaps.append("Executive summary is too short for a decision-ready brief.")
        if not brief.assumptions:
            gaps.append("Brief does not identify assumptions.")
        if not brief.next_actions:
            gaps.append("Brief does not contain next actions.")
        if not any(claim.importance == "material" for claim in brief.claims):
            gaps.append("Brief contains no material claim.")
        return gaps
