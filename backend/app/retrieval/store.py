from __future__ import annotations

import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import stable_hash
from app.db.models import KnowledgeDocumentModel
from app.domain.schemas import KnowledgeDocumentRequest, KnowledgeDocumentResponse
from app.fixtures.demo_documents import DEMO_DOCUMENTS
from app.retrieval.hybrid import RetrievalDocument


class KnowledgeStore:
    """Tenant-aware document store with idempotent seed behavior."""

    def seed_demo_documents(self, session: Session, tenant_id: str) -> None:
        existing = set(
            session.scalars(
                select(KnowledgeDocumentModel.document_id).where(KnowledgeDocumentModel.tenant_id == tenant_id)
            ).all()
        )
        for document in DEMO_DOCUMENTS:
            if document.document_id in existing:
                continue
            session.add(
                KnowledgeDocumentModel(
                    tenant_id=tenant_id,
                    document_id=document.document_id,
                    title=document.title,
                    source_type=document.source_type,
                    content=document.content,
                    metadata_json=document.metadata,
                    content_hash=stable_hash(document.content),
                )
            )
        session.commit()

    def upsert(self, session: Session, tenant_id: str, request: KnowledgeDocumentRequest) -> KnowledgeDocumentResponse:
        statement = select(KnowledgeDocumentModel).where(
            KnowledgeDocumentModel.tenant_id == tenant_id,
            KnowledgeDocumentModel.document_id == request.document_id,
        )
        record = session.scalar(statement)
        content_hash = hashlib.sha256(request.content.encode("utf-8")).hexdigest()
        if record is None:
            record = KnowledgeDocumentModel(
                tenant_id=tenant_id,
                document_id=request.document_id,
                title=request.title,
                source_type=request.source_type,
                content=request.content,
                metadata_json=request.metadata,
                content_hash=content_hash,
            )
            session.add(record)
        else:
            record.title = request.title
            record.source_type = request.source_type
            record.content = request.content
            record.metadata_json = request.metadata
            record.content_hash = content_hash
        session.commit()
        session.refresh(record)
        return KnowledgeDocumentResponse(
            document_id=record.document_id,
            title=record.title,
            source_type=record.source_type,
            content_hash=record.content_hash,
            created_at=record.created_at,
        )

    def list_for_tenant(self, session: Session, tenant_id: str) -> list[RetrievalDocument]:
        records = session.scalars(
            select(KnowledgeDocumentModel)
            .where(KnowledgeDocumentModel.tenant_id == tenant_id)
            .order_by(KnowledgeDocumentModel.created_at.asc())
        ).all()
        return [
            RetrievalDocument(
                document_id=record.document_id,
                title=record.title,
                source_type=record.source_type,
                content=record.content,
                metadata={str(key): str(value) for key, value in record.metadata_json.items()},
            )
            for record in records
        ]
