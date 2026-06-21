from app.core.config import get_settings
from app.db.session import SessionLocal, initialize_database
from app.domain.schemas import EvaluationRunRequest
from app.evaluation.runner import EvaluationRunner
from app.retrieval.store import KnowledgeStore


def test_taskbench_runs_and_returns_profile_summary() -> None:
    settings = get_settings()
    initialize_database()
    with SessionLocal() as session:
        KnowledgeStore().seed_demo_documents(session, settings.default_tenant_id)
        result = EvaluationRunner(settings).run(
            session,
            EvaluationRunRequest(
                model_profiles=["enterprise-balanced"],
                task_ids=["vendor-selection-001", "vendor-selection-003"],
            ),
        )
    assert result.status == "completed"
    assert len(result.results) == 2
    assert result.summary["best_profile"] == "enterprise-balanced"
