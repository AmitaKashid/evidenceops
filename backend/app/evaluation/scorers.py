from __future__ import annotations

from dataclasses import dataclass

from app.domain.schemas import DecisionBrief, EvaluationCase, VerificationResult


@dataclass(frozen=True)
class ScoreBundle:
    task_completion: float
    citation_coverage: float
    numeric_accuracy: float
    escalation_correctness: float
    composite_score: float
    notes: list[str]


class EvaluationScorer:
    """Scores both output utility and reliability controls.

    The scoring intentionally reuses the deterministic verifier rather than asking
    another model to judge itself. Human review can later be added as a separate
    adjudication column, not silently mixed into automated metrics.
    """

    def score(
        self,
        *,
        case: EvaluationCase,
        brief: DecisionBrief,
        verification: VerificationResult,
    ) -> ScoreBundle:
        notes: list[str] = []
        text = " ".join(
            [brief.executive_summary, brief.recommendation]
            + brief.rationale
            + [claim.statement for claim in brief.claims]
            + brief.unresolved_questions
        ).lower()

        required_fragments = case.expected_claim_fragments
        matched_fragments = sum(fragment.lower() in text for fragment in required_fragments)
        fragment_score = matched_fragments / max(len(required_fragments), 1)

        vendor_score = 1.0
        if case.expected_vendor:
            vendor_score = 1.0 if case.expected_vendor.lower() in text else 0.0
            if not vendor_score:
                notes.append(f"Expected vendor {case.expected_vendor} was not present in the output.")

        used_documents = {
            citation.document_id
            for claim in brief.claims
            for citation in claim.citations
        }
        expected_docs = set(case.expected_document_ids)
        evidence_score = len(used_documents & expected_docs) / max(len(expected_docs), 1)
        if evidence_score < 1.0:
            notes.append("Not all expected source documents were represented in material claims.")

        escalation_score = float(verification.escalation_required == case.expected_escalation)
        if not escalation_score:
            notes.append("Escalation outcome did not match the labelled task expectation.")

        task_completion = (0.40 * fragment_score) + (0.35 * vendor_score) + (0.25 * evidence_score)
        composite = (
            (0.34 * task_completion)
            + (0.28 * verification.citation_coverage)
            + (0.20 * verification.numeric_accuracy)
            + (0.18 * escalation_score)
        )
        return ScoreBundle(
            task_completion=round(task_completion, 3),
            citation_coverage=verification.citation_coverage,
            numeric_accuracy=verification.numeric_accuracy,
            escalation_correctness=escalation_score,
            composite_score=round(composite, 3),
            notes=notes,
        )
