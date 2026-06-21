from __future__ import annotations

from typing import Any

from app.core.config import Settings
from app.domain.schemas import TaskContract
from app.llm.base import DecisionModelProvider
from app.retrieval.hybrid import HybridRetriever, RetrievedChunk
from app.tools.spreadsheet import PricingAnalysisTool
from app.tools.web_research import GuardedResearchTool
from app.verification.claims import ClaimVerifier
from app.verification.quality import BriefQualityRules
from app.workflow.state import WorkflowState


class WorkflowNodes:
    """Small, typed node implementations used by the LangGraph state graph.

    Nodes do not perform persistence themselves. The orchestration service records
    state and events between stages, which keeps each action testable and makes the
    storage policy explicit.
    """

    def __init__(
        self,
        *,
        settings: Settings,
        retriever: HybridRetriever,
        provider: DecisionModelProvider,
        pricing_tool: PricingAnalysisTool,
        research_tool: GuardedResearchTool,
    ) -> None:
        self.settings = settings
        self.retriever = retriever
        self.provider = provider
        self.pricing_tool = pricing_tool
        self.research_tool = research_tool
        self.claim_verifier = ClaimVerifier()
        self.quality_rules = BriefQualityRules()

    def build_contract(self, state: WorkflowState) -> WorkflowState:
        request = state["user_request"]
        lowered = request.lower()
        capabilities = ["document_retrieval", "decision_brief_generation", "citation_verification"]
        if any(term in lowered for term in ("cost", "price", "pricing", "tco", "total cost")):
            capabilities.append("spreadsheet_analysis")
        if any(term in lowered for term in ("current", "public", "regulation", "external", "web")):
            capabilities.append("guarded_research")
        contract = TaskContract(
            objective=request.strip(),
            deliverable="Evidence-grounded management decision brief",
            required_capabilities=capabilities,
            allowed_source_types=["internal", "pricing", "public_research"],
            approval_required=bool(state.get("require_human_review", True)),
            escalation_conditions=[
                "Material claim lacks approved evidence.",
                "Pricing or numerical output cannot be reconciled.",
                "Source documents conflict on mandatory controls.",
                "A conclusion requires assumptions beyond the approved sources.",
            ],
            quality_bar=[
                "Every material claim has at least one evidence citation.",
                "Numeric claims are reconciled against deterministic tool output.",
                "The decision brief lists assumptions, trade-offs, and next actions.",
            ],
            constraints=[
                "Read-only workflow: no external action is executed.",
                "Only tenant-approved sources may be retrieved.",
                "Human review is required for consequential decisions.",
            ],
        )
        return {"contract": contract.model_dump(mode="json"), "status": "running"}

    def retrieve_evidence(self, state: WorkflowState) -> WorkflowState:
        contract = TaskContract.model_validate(state["contract"])
        query = f"{contract.objective} {' '.join(contract.quality_bar)}"
        chunks = self.retriever.retrieve(
            query,
            allowed_document_ids=state.get("allowed_document_ids") or None,
            max_results=self.settings.maximum_retrieval_documents,
        )
        if not chunks:
            raise ValueError("No approved evidence was retrieved for this task.")
        return {"retrieved_evidence": [self._serialize_chunk(chunk) for chunk in chunks]}

    def analyze_pricing(self, state: WorkflowState) -> WorkflowState:
        contract = TaskContract.model_validate(state["contract"])
        if "spreadsheet_analysis" not in contract.required_capabilities:
            return {"pricing_results": []}
        return {"pricing_results": [result.to_dict() for result in self.pricing_tool.calculate_three_year_tco()]}

    def research(self, state: WorkflowState) -> WorkflowState:
        contract = TaskContract.model_validate(state["contract"])
        if "guarded_research" not in contract.required_capabilities:
            return {"research_results": []}
        results = self.research_tool.search(contract.objective)
        return {
            "research_results": [
                {"title": item.title, "url": item.url, "summary": item.summary, "allowed": item.allowed}
                for item in results
            ]
        }

    def draft_brief(self, state: WorkflowState) -> WorkflowState:
        contract = TaskContract.model_validate(state["contract"])
        evidence = [self._deserialize_chunk(item) for item in state.get("retrieved_evidence", [])]
        brief = self.provider.compose_decision_brief(
            contract=contract,
            evidence=evidence,
            pricing=state.get("pricing_results", []),
            profile=state["model_profile"],
        )
        return {"decision_brief": brief.model_dump(mode="json")}

    def verify_brief(self, state: WorkflowState) -> WorkflowState:
        from app.domain.schemas import DecisionBrief

        brief = DecisionBrief.model_validate(state["decision_brief"])
        evidence = [self._deserialize_chunk(item) for item in state.get("retrieved_evidence", [])]
        known_sources = {chunk.chunk_id: chunk.as_reference() for chunk in evidence}
        pricing = {item["vendor"]: item for item in state.get("pricing_results", [])}
        result = self.claim_verifier.verify(brief, known_sources, pricing)
        quality_gaps = self.quality_rules.assess(brief)
        if quality_gaps:
            from app.domain.enums import VerificationSeverity
            from app.domain.schemas import VerificationIssue

            result.issues.extend(
                VerificationIssue(
                    rule_id="brief.completeness",
                    severity=VerificationSeverity.WARNING,
                    message=gap,
                    remediation="Update the draft before final approval.",
                )
                for gap in quality_gaps
            )
            result.quality_score = round(max(0.0, result.quality_score - (0.03 * len(quality_gaps))), 3)
        return {
            "verification": result.model_dump(mode="json"),
            "quality_gaps": quality_gaps,
            "status": "waiting_for_review" if state.get("require_human_review", True) else "approved",
        }

    @staticmethod
    def _serialize_chunk(chunk: RetrievedChunk) -> dict[str, Any]:
        return {
            "document_id": chunk.document_id,
            "chunk_id": chunk.chunk_id,
            "title": chunk.title,
            "section": chunk.section,
            "content": chunk.content,
            "source_type": chunk.source_type,
            "score": chunk.score,
        }

    @staticmethod
    def _deserialize_chunk(value: dict[str, Any]) -> RetrievedChunk:
        return RetrievedChunk(
            document_id=str(value["document_id"]),
            chunk_id=str(value["chunk_id"]),
            title=str(value["title"]),
            section=str(value["section"]),
            content=str(value["content"]),
            source_type=str(value["source_type"]),
            score=float(value["score"]),
        )
