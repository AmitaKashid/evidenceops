from app.domain.schemas import DecisionBrief, DecisionClaim, SourceReference
from app.verification.claims import ClaimVerifier


def test_verifier_rejects_unknown_citation() -> None:
    citation = SourceReference(
        document_id="unknown",
        chunk_id="unknown::chunk::0",
        title="Unknown source",
        section="General",
        excerpt="Untrusted source text.",
        score=0.9,
        source_type="internal",
    )
    brief = DecisionBrief(
        executive_summary="This summary is sufficiently detailed to be a basic decision brief for test coverage.",
        recommendation="Proceed only after evidence review.",
        rationale=["A source should support the material conclusion."],
        findings=[],
        claims=[
            DecisionClaim(
                claim_id="material-1",
                statement="Northstar is recommended.",
                importance="material",
                citations=[citation],
                confidence=0.8,
            )
        ],
        assumptions=["None"],
        unresolved_questions=[],
        next_actions=["Review evidence"],
        generated_by="test",
    )
    result = ClaimVerifier().verify(brief, {}, {})

    assert result.passed is False
    assert any(issue.rule_id == "citation.unknown_source" for issue in result.issues)
