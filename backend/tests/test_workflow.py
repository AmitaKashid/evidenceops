from app.core.config import get_settings
from app.db.session import SessionLocal, initialize_database
from app.domain.schemas import TaskRequest
from app.services.task_service import TaskOrchestrator


def test_task_workflow_creates_reviewable_evidence_grounded_run() -> None:
    settings = get_settings()
    initialize_database()
    with SessionLocal() as session:
        run = TaskOrchestrator(settings).execute(
            session,
            TaskRequest(
                title="Vendor selection test",
                request=(
                    "Review the approved vendor documents, compare vendors against internal security requirements, "
                    "calculate a three-year total cost of ownership, identify policy gaps, and prepare a management "
                    "decision brief with evidence citations. Escalate any unsupported conclusion."
                ),
            ),
        )

    assert run.status == "waiting_for_review"
    assert run.decision_brief is not None
    assert run.verification is not None
    assert run.decision_brief.claims
    assert run.verification.numeric_accuracy == 1.0
    assert any(event.stage == "verify_brief" for event in run.events)
