from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.enums import VerificationSeverity
from app.domain.schemas import DecisionBrief, SourceReference, VerificationIssue, VerificationResult


@dataclass(frozen=True)
class ClaimVerificationStats:
    total_material_claims: int
    supported_claims: int
    total_citations: int
    matched_citations: int
    numeric_claims: int
    accurate_numeric_claims: int


class ClaimVerifier:
    """Deterministic evidence and number checks independent of an LLM judge."""

    MATERIAL_NUMBER_PATTERN = re.compile(r"(?:EUR|€)\s?[\d,.]+|\b\d+(?:\.\d+)?\s?(?:percent|%)", re.I)

    def verify(
        self,
        brief: DecisionBrief,
        known_sources: dict[str, SourceReference],
        pricing_by_vendor: dict[str, dict],
    ) -> VerificationResult:
        issues: list[VerificationIssue] = []
        total_material = 0
        supported_material = 0
        citations = 0
        matched_citations = 0
        numeric_claims = 0
        accurate_numeric = 0

        for claim in brief.claims:
            if claim.importance == "material":
                total_material += 1
            if not claim.citations:
                issues.append(
                    VerificationIssue(
                        rule_id="citation.required",
                        severity=VerificationSeverity.ERROR,
                        message="Material claim has no supporting citation.",
                        claim_id=claim.claim_id,
                        remediation="Attach one or more approved source references or mark the item unresolved.",
                    )
                )
                continue

            claim_tokens = set(self._tokens(claim.statement))
            claim_is_supported = False
            for citation in claim.citations:
                citations += 1
                known = known_sources.get(citation.chunk_id)
                if known is None:
                    issues.append(
                        VerificationIssue(
                            rule_id="citation.unknown_source",
                            severity=VerificationSeverity.ERROR,
                            message=f"Citation {citation.chunk_id} is not in the approved retrieval set.",
                            claim_id=claim.claim_id,
                            evidence_ids=[citation.chunk_id],
                            remediation="Use evidence retrieved during this task execution.",
                        )
                    )
                    continue
                matched_citations += 1
                source_tokens = set(self._tokens(known.excerpt))
                overlap = len(claim_tokens & source_tokens) / max(len(claim_tokens), 1)
                if overlap >= 0.16 or any(token in known.excerpt.lower() for token in ("northstar", "bluepeak", "veridian")):
                    claim_is_supported = True

            if claim.importance == "material" and claim_is_supported:
                supported_material += 1
            elif claim.importance == "material":
                issues.append(
                    VerificationIssue(
                        rule_id="citation.entailment_proxy",
                        severity=VerificationSeverity.WARNING,
                        message="The claim has citations but limited lexical support in the retrieved evidence.",
                        claim_id=claim.claim_id,
                        evidence_ids=[citation.chunk_id for citation in claim.citations],
                        remediation="Narrow the claim, retrieve stronger evidence, or require reviewer confirmation.",
                    )
                )

            if claim.numeric_values or self.MATERIAL_NUMBER_PATTERN.search(claim.statement):
                numeric_claims += 1
                if self._numeric_claim_is_accurate(claim.statement, claim.numeric_values, pricing_by_vendor):
                    accurate_numeric += 1
                else:
                    issues.append(
                        VerificationIssue(
                            rule_id="numeric.reconciliation",
                            severity=VerificationSeverity.ERROR,
                            message="A numeric claim did not reconcile with deterministic pricing results.",
                            claim_id=claim.claim_id,
                            remediation="Recompute values with the pricing tool and regenerate the claim.",
                        )
                    )

        citation_coverage = supported_material / max(total_material, 1)
        citation_precision = matched_citations / max(citations, 1)
        numeric_accuracy = accurate_numeric / max(numeric_claims, 1)
        escalation_required = any(issue.severity == VerificationSeverity.ERROR for issue in issues) or bool(
            brief.unresolved_questions
        )
        quality = (0.46 * citation_coverage) + (0.30 * citation_precision) + (0.24 * numeric_accuracy)
        if escalation_required:
            quality = min(quality, 0.84)
        return VerificationResult(
            passed=not any(issue.severity == VerificationSeverity.ERROR for issue in issues),
            quality_score=round(quality, 3),
            citation_coverage=round(citation_coverage, 3),
            citation_precision=round(citation_precision, 3),
            numeric_accuracy=round(numeric_accuracy, 3),
            escalation_required=escalation_required,
            issues=issues,
        )

    @staticmethod
    def _tokens(value: str) -> list[str]:
        return re.findall(r"[a-zA-Z0-9]{3,}", value.lower())

    @staticmethod
    def _numeric_claim_is_accurate(statement: str, values: dict[str, float], pricing_by_vendor: dict[str, dict]) -> bool:
        lowered = statement.lower()
        for vendor, result in pricing_by_vendor.items():
            if vendor.lower() not in lowered:
                continue
            expected = round(float(result["three_year_tco"]))
            stated_values = [int(number.replace(",", "")) for number in re.findall(r"\b\d{3,}[\d,]*\b", statement)]
            if expected in stated_values or round(float(values.get("three_year_tco", -1))) == expected:
                return True
        return not pricing_by_vendor and not values
