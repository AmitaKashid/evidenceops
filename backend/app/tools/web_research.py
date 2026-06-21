from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchResult:
    title: str
    url: str
    summary: str
    allowed: bool


class GuardedResearchTool:
    """A deliberately narrow research abstraction.

    The local demo returns only curated summaries. A production implementation
    should place web retrieval behind allow-lists, content scanning, caching,
    attribution controls, and organization-specific network policy.
    """

    def search(self, query: str) -> list[ResearchResult]:
        normalized = query.lower()
        results: list[ResearchResult] = []
        if any(term in normalized for term in ("eu", "governance", "security", "residency")):
            results.append(
                ResearchResult(
                    title="Controlled public research note",
                    url="https://example.invalid/evidenceops/research-note",
                    summary=(
                        "Enterprise procurement should document data residency, access control, auditability, "
                        "assurance evidence, and incident governance. This offline result is illustrative only."
                    ),
                    allowed=True,
                )
            )
        return results
