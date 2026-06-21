from __future__ import annotations

from app.core.config import get_settings
from app.db.session import SessionLocal, initialize_database
from app.retrieval.store import KnowledgeStore


def main() -> None:
    settings = get_settings()
    initialize_database()
    with SessionLocal() as session:
        KnowledgeStore().seed_demo_documents(session, settings.default_tenant_id)
    print("Seeded EvidenceOps demo corpus.")


if __name__ == "__main__":
    main()
