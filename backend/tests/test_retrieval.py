from app.fixtures.demo_documents import DEMO_DOCUMENTS
from app.retrieval.hybrid import HybridRetriever, RetrievalDocument


def test_hybrid_retrieval_prioritizes_security_requirements() -> None:
    documents = [
        RetrievalDocument(
            document_id=item.document_id,
            title=item.title,
            source_type=item.source_type,
            content=item.content,
            metadata=item.metadata,
        )
        for item in DEMO_DOCUMENTS
    ]
    results = HybridRetriever(documents).retrieve(
        "Which vendor supports SAML single sign-on SOC 2 Type II EEA data residency and audit logs?",
        max_results=5,
    )
    ids = {item.document_id for item in results}

    assert "vendor_northstar_security_2026" in ids
    assert "internal_security_requirements_v1" in ids
    assert all(result.score > 0 for result in results)
