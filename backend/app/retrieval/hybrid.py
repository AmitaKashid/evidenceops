from __future__ import annotations

import math
import re
from dataclasses import dataclass

from app.domain.schemas import SourceReference
from app.retrieval.tokenizer import inverse_document_frequency, term_frequencies, tokenize


@dataclass(frozen=True)
class RetrievalDocument:
    document_id: str
    title: str
    source_type: str
    content: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: str
    chunk_id: str
    title: str
    section: str
    content: str
    source_type: str
    score: float

    def as_reference(self) -> SourceReference:
        return SourceReference(
            document_id=self.document_id,
            chunk_id=self.chunk_id,
            title=self.title,
            section=self.section,
            excerpt=self.content[:1000],
            score=round(max(0.0, min(self.score, 1.0)), 3),
            source_type=self.source_type,  # type: ignore[arg-type]
        )


class HybridRetriever:
    """Dependency-free hybrid ranking suitable for a deterministic demo.

    The score combines BM25-inspired lexical relevance, phrase overlap, section
    priors, and a light semantic proxy based on token-set overlap. In production,
    the same interface can be backed by pgvector or a managed vector store.
    """

    def __init__(self, documents: list[RetrievalDocument], chunk_size: int = 850) -> None:
        self.documents = documents
        self.chunk_size = chunk_size
        self.chunks = self._chunk_documents(documents)
        self.idf = inverse_document_frequency([chunk.content for chunk in self.chunks])
        self.average_length = max(
            sum(len(tokenize(chunk.content)) for chunk in self.chunks) / max(len(self.chunks), 1), 1
        )

    @staticmethod
    def _section_name(content: str, fallback: str) -> str:
        for line in content.splitlines():
            if line.startswith("## "):
                return line.removeprefix("## ").strip()
            if line.startswith("# "):
                return line.removeprefix("# ").strip()
        return fallback

    def _chunk_documents(self, documents: list[RetrievalDocument]) -> list[RetrievedChunk]:
        chunks: list[RetrievedChunk] = []
        for document in documents:
            paragraphs = [part.strip() for part in re.split(r"\n\s*\n", document.content) if part.strip()]
            buffer: list[str] = []
            current_size = 0
            index = 0
            for paragraph in paragraphs:
                if current_size + len(paragraph) > self.chunk_size and buffer:
                    text = "\n\n".join(buffer)
                    chunks.append(
                        RetrievedChunk(
                            document_id=document.document_id,
                            chunk_id=f"{document.document_id}::chunk::{index}",
                            title=document.title,
                            section=self._section_name(text, "General"),
                            content=text,
                            source_type=document.source_type,
                            score=0.0,
                        )
                    )
                    index += 1
                    buffer, current_size = [], 0
                buffer.append(paragraph)
                current_size += len(paragraph)
            if buffer:
                text = "\n\n".join(buffer)
                chunks.append(
                    RetrievedChunk(
                        document_id=document.document_id,
                        chunk_id=f"{document.document_id}::chunk::{index}",
                        title=document.title,
                        section=self._section_name(text, "General"),
                        content=text,
                        source_type=document.source_type,
                        score=0.0,
                    )
                )
        return chunks

    def retrieve(
        self,
        query: str,
        *,
        allowed_document_ids: list[str] | None = None,
        max_results: int = 8,
    ) -> list[RetrievedChunk]:
        query_tokens = tokenize(query)
        query_terms = set(query_tokens)
        allowed = set(allowed_document_ids or [])
        candidates = [
            chunk for chunk in self.chunks if not allowed or chunk.document_id in allowed
        ]
        scored: list[RetrievedChunk] = []
        for chunk in candidates:
            frequencies = term_frequencies(chunk.content)
            length = max(sum(frequencies.values()), 1)
            bm25 = 0.0
            for term in query_terms:
                frequency = frequencies.get(term, 0)
                if not frequency:
                    continue
                k1, b = 1.35, 0.7
                denominator = frequency + k1 * (1 - b + b * (length / self.average_length))
                bm25 += self.idf.get(term, 0.0) * ((frequency * (k1 + 1)) / denominator)

            chunk_terms = set(frequencies)
            overlap = len(query_terms & chunk_terms) / max(len(query_terms), 1)
            lowered = chunk.content.lower()
            phrase_bonus = sum(0.12 for phrase in self._important_phrases(query) if phrase in lowered)
            source_bonus = 0.04 if chunk.source_type == "internal" else 0.0
            section_bonus = 0.03 if any(keyword in chunk.section.lower() for keyword in query_terms) else 0.0
            raw_score = (0.52 * self._normalize_bm25(bm25)) + (0.35 * overlap) + phrase_bonus + source_bonus + section_bonus
            scored.append(
                RetrievedChunk(
                    document_id=chunk.document_id,
                    chunk_id=chunk.chunk_id,
                    title=chunk.title,
                    section=chunk.section,
                    content=chunk.content,
                    source_type=chunk.source_type,
                    score=min(raw_score, 1.0),
                )
            )
        return sorted(scored, key=lambda item: item.score, reverse=True)[:max_results]

    @staticmethod
    def _important_phrases(query: str) -> list[str]:
        phrases = re.findall(r"(?:[a-zA-Z]+\s+){1,3}[a-zA-Z]+", query.lower())
        return [phrase.strip() for phrase in phrases if len(phrase.strip().split()) >= 2][:8]

    @staticmethod
    def _normalize_bm25(value: float) -> float:
        return 1 - math.exp(-max(value, 0.0) / 3.5)
