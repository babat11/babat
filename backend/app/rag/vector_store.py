"""Vector store abstraction (placeholder).

This defines a clean interface for a vector store backing future
retrieval-augmented generation (RAG). It is intentionally NOT a working vector
database yet.

TODO(pgvector): Implement a PostgreSQL + pgvector backend:
    * Use SQLAlchemy async engine with the ``vector`` column type.
    * Store embeddings produced by an embedding model (e.g. text-embedding-3).
    * Implement cosine/L2 similarity search via pgvector operators.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """A single document/chunk stored in the vector store."""

    id: str
    text: str
    metadata: dict[str, str] = field(default_factory=dict)
    embedding: list[float] | None = None


@dataclass
class SearchResult:
    """A search hit with its similarity score."""

    document: Document
    score: float


class VectorStore(ABC):
    """Abstract interface for a vector store."""

    @abstractmethod
    async def add_documents(self, documents: list[Document]) -> None:
        """Add (and embed, if needed) documents to the store."""
        raise NotImplementedError

    @abstractmethod
    async def similarity_search(
        self, query: str, top_k: int = 5
    ) -> list[SearchResult]:
        """Return the ``top_k`` most similar documents to ``query``."""
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> bool:
        """Return whether the store is reachable/ready."""
        raise NotImplementedError


class InMemoryVectorStore(VectorStore):
    """A no-op, in-memory placeholder implementation.

    This stores documents in a list and returns naive substring matches. It
    exists only so the rest of the application can depend on the interface
    during development. It is NOT suitable for production retrieval.

    TODO(pgvector): Replace with a real embedding-backed implementation.
    """

    def __init__(self) -> None:
        self._documents: list[Document] = []

    async def add_documents(self, documents: list[Document]) -> None:
        logger.debug("InMemoryVectorStore: adding %d documents", len(documents))
        self._documents.extend(documents)

    async def similarity_search(
        self, query: str, top_k: int = 5
    ) -> list[SearchResult]:
        # Placeholder: naive case-insensitive substring scoring.
        q = query.lower()
        scored: list[SearchResult] = []
        for doc in self._documents:
            score = 1.0 if q in doc.text.lower() else 0.0
            if score > 0:
                scored.append(SearchResult(document=doc, score=score))
        return scored[:top_k]

    async def health_check(self) -> bool:
        return True
