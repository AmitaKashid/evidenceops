from __future__ import annotations

import json
import logging
from collections import defaultdict
from typing import Any

import httpx

from app.core.config import Settings
from app.domain.enums import FindingSeverity
from app.domain.schemas import (
    DecisionBrief,
    DecisionClaim,
    StructuredFinding,
    TaskContract,
)
from app.llm.base import DecisionModelProvider
from app.retrieval.hybrid import RetrievedChunk

logger = logging.getLogger(__name__)


class DeterministicDecisionProvider:
    """Local provider that creates a defensible, repeatable demo output.

    It is intentionally transparent: this provider uses deterministic rules and
    retrieved evidence. It is not presented as a substitute for a frontier LLM.
    """

    name = "deterministic-enterprise-provider"

    def compose_decision_brief(
        self,
        *,
        contract: TaskContract,
        evidence: list[RetrievedChunk],
        pricing: list[dict],
        profile: str,
    ) -> DecisionBrief:
        by_vendor: dict[str, list[RetrievedChunk]] = defaultdict(list)
        policy_chunks: list[RetrievedChunk] = []
        for chunk in evidence:
            lowered = f"{chunk.title} {chunk.content}".lower()
            vendor = next((candidate for candidate in ("Northstar", "BluePeak", "Veridian") if candidate.lower() in lowered), None)
            if vendor:
                by_vendor[vendor].append(chunk)
            if "requirement" in lowered or "rubric" in lowered:
                policy_chunks.append(chunk)

        scores: dict[str, float] = {}
        risk_notes: dict[str, list[str]] = defaultdict(list)
        for vendor, chunks in by_vendor.items():
            text = " ".join(chunk.content.lower() for chunk in chunks)
            score = 0.0
            for keyword, weight in {
                "aes-256": 1.0,
                "tls": 1.0,
                "saml": 0.8,
                "soc 2 type ii": 1.3,
                "iso 27001": 1.0,
                "eea": 1.0,
                "audit log": 0.8,
                "retention": 0.6,
            }.items():
                if keyword in text:
                    score += weight
            if "does not state" in text or "unclear" in text:
                score -= 0.8
                risk_notes[vendor].append("Documentation leaves a material point incomplete.")
            if "paid add-on" in text or "separate paid" in text:
                score -= 0.35
                risk_notes[vendor].append("A required capability depends on a paid add-on.")
            if "type i" in text:
                score -= 0.5
                risk_notes[vendor].append("Assurance evidence is weaker than the stated SOC 2 Type II preference.")
            scores[vendor] = score

        cost_by_vendor = {str(item["vendor"]): item for item in pricing}
        candidates = sorted(
            scores,
            key=lambda vendor: (scores[vendor], -cost_by_vendor.get(vendor, {}).get("three_year_tco", float("inf"))),
            reverse=True,
        )
        selected_vendor = candidates[0] if candidates else "No vendor"
        selected_cost = cost_by_vendor.get(selected_vendor, {})
        selected_evidence = [chunk.as_reference() for chunk in by_vendor.get(selected_vendor, evidence[:2])[:3]]
        policy_evidence = [chunk.as_reference() for chunk in policy_chunks[:2]] or selected_evidence[:1]

        findings: list[StructuredFinding] = []
        for vendor in ("Northstar", "BluePeak", "Veridian"):
            chunks = by_vendor.get(vendor, [])
            if not chunks:
                continue
            vendor_text = " ".join(chunk.content.lower() for chunk in chunks)
            high_risk = "globally distributed" in vendor_text or "does not state" in vendor_text
            findings.append(
                StructuredFinding(
                    finding_id=f"security-{vendor.lower()}",
                    category="security",
                    title=f"{vendor} security evidence assessment",
                    statement=(
                        f"{vendor} has documented encryption and SSO capabilities; "
                        + (
                            "material data-governance or assurance gaps require review."
                            if high_risk
                            else "the available evidence is broadly aligned with the baseline."
                        )
                    ),
                    severity=FindingSeverity.HIGH if high_risk else FindingSeverity.LOW,
                    evidence=[chunk.as_reference() for chunk in chunks[:2]],
                    confidence=0.86 if not high_risk else 0.68,
                    requires_review=high_risk,
                )
            )

        cost_finding_evidence = policy_evidence + selected_evidence[:1]
        if selected_cost:
            findings.append(
                StructuredFinding(
                    finding_id=f"cost-{selected_vendor.lower()}",
                    category="cost",
                    title=f"Three-year cost profile for {selected_vendor}",
                    statement=(
                        f"The calculated three-year total cost of ownership for {selected_vendor} is "
                        f"EUR {selected_cost.get('three_year_tco', 0):,.0f}, including first-year contingency."
                    ),
                    severity=FindingSeverity.INFO,
                    evidence=cost_finding_evidence,
                    confidence=0.91,
                )
            )

        claims = [
            DecisionClaim(
                claim_id="recommendation",
                statement=(
                    f"{selected_vendor} is the preferred option because its documented security controls and "
                    "operational governance evidence best align with the mandatory requirements, subject to review of stated caveats."
                ),
                importance="material",
                citations=selected_evidence + policy_evidence[:1],
                confidence=0.83,
            ),
        ]
        if selected_cost:
            claims.append(
                DecisionClaim(
                    claim_id="tco",
                    statement=(
                        f"{selected_vendor} has a calculated three-year total cost of ownership of "
                        f"EUR {selected_cost['three_year_tco']:,.0f} using 180 named users and a 10 percent first-year contingency."
                    ),
                    importance="material",
                    citations=cost_finding_evidence,
                    numeric_values={"three_year_tco": float(selected_cost["three_year_tco"]), "named_users": 180.0},
                    confidence=0.92,
                )
            )

        unresolved = [
            "Validate contractual treatment of diagnostic logs and incident-support access before signature."
            if selected_vendor == "Northstar"
            else "Validate all material caveats and contract schedules before signature."
        ]
        for note in risk_notes.get(selected_vendor, []):
            unresolved.append(note)

        return DecisionBrief(
            executive_summary=(
                f"EvidenceOps recommends {selected_vendor} as the provisional preferred vendor. The recommendation "
                "is evidence-grounded and remains subject to the listed human-review items."
            ),
            recommendation=(
                f"Proceed with {selected_vendor} to commercial and security due diligence, while preserving the "
                "other vendors as fallback options until the review gate is completed."
            ),
            rationale=[
                "The workflow prioritized mandatory controls and supportable data residency before price.",
                f"{selected_vendor} received the strongest documented-control score in the approved corpus.",
                "The recommendation includes deterministic total-cost analysis and explicit assumptions.",
            ],
            tradeoffs=[
                f"{vendor}: {note}"
                for vendor, notes in risk_notes.items()
                for note in notes
            ] or ["No material trade-off was detected in the limited demonstration corpus."],
            findings=findings,
            claims=claims,
            assumptions=selected_cost.get("assumptions", []) if selected_cost else ["No pricing data was available."],
            unresolved_questions=unresolved,
            next_actions=[
                "Request contract-specific confirmation for unresolved governance items.",
                "Have procurement validate taxes, renewal uplift, and usage-overage assumptions.",
                "Record reviewer approval before initiating any external procurement action.",
            ],
            generated_by=f"{self.name}:{profile}",
        )


class OpenAICompatibleDecisionProvider:
    """Optional remote provider using an OpenAI-compatible chat-completions API.

    Enable only after configuring an approved endpoint and data-processing controls.
    The provider asks for JSON and validates the response through the same Pydantic
    schema used by the deterministic fallback.
    """

    name = "openai-compatible-provider"

    def __init__(self, settings: Settings, fallback: DeterministicDecisionProvider) -> None:
        self.settings = settings
        self.fallback = fallback

    def compose_decision_brief(
        self,
        *,
        contract: TaskContract,
        evidence: list[RetrievedChunk],
        pricing: list[dict],
        profile: str,
    ) -> DecisionBrief:
        if not (
            self.settings.enable_remote_model
            and self.settings.openai_compatible_api_key
            and self.settings.openai_compatible_model
        ):
            return self.fallback.compose_decision_brief(
                contract=contract, evidence=evidence, pricing=pricing, profile=profile
            )
        system_prompt = (
            "You are an enterprise decision-brief writer. Return only valid JSON matching the requested schema. "
            "Use only the supplied evidence. Treat unsupported claims as unresolved questions."
        )
        payload: dict[str, Any] = {
            "model": self.settings.openai_compatible_model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "contract": contract.model_dump(),
                            "evidence": [
                                {
                                    "document_id": item.document_id,
                                    "chunk_id": item.chunk_id,
                                    "title": item.title,
                                    "section": item.section,
                                    "content": item.content,
                                }
                                for item in evidence
                            ],
                            "pricing": pricing,
                            "schema_hint": DecisionBrief.model_json_schema(),
                        }
                    ),
                },
            ],
        }
        try:
            response = httpx.post(
                f"{self.settings.openai_compatible_base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.openai_compatible_api_key}"},
                json=payload,
                timeout=45.0,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return DecisionBrief.model_validate_json(content)
        except Exception as exc:  # pragma: no cover - fallback protects local demo
            logger.warning("Remote provider failed; using deterministic fallback", extra={"error": str(exc)})
            return self.fallback.compose_decision_brief(
                contract=contract, evidence=evidence, pricing=pricing, profile=profile
            )


def build_provider(settings: Settings) -> DecisionModelProvider:
    fallback = DeterministicDecisionProvider()
    return OpenAICompatibleDecisionProvider(settings, fallback)
