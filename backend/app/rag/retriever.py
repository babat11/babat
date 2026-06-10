"""Retriever abstraction (placeholder).

Provides a clean interface for retrieving relevant legal context to augment LLM
prompts in the future. It is intentionally a thin wrapper over a
:class:`~app.rag.vector_store.VectorStore` and is NOT wired into the analysis
pipeline yet.

TODO(pgvector): Once the pgvector-backed VectorStore is implemented, inject the
retrieved snippets into the analyze/letter prompts as grounding context.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from app.rag.vector_store import (
    InMemoryVectorStore,
    SearchResult,
    VectorStore,
)

logger = logging.getLogger(__name__)


class Retriever(ABC):
    """Abstract interface for retrieving relevant context."""

    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Return relevant documents for ``query``."""
        raise NotImplementedError


class VectorStoreRetriever(Retriever):
    """A retriever backed by a :class:`VectorStore`.

    TODO(pgvector): Add query pre-processing, re-ranking, and metadata
    filtering (e.g. by jurisdiction or law category).
    """

    def __init__(self, vector_store: VectorStore | None = None) -> None:
        self._vector_store = vector_store or InMemoryVectorStore()

    async def retrieve(self, query: str, top_k: int = 5) -> list[SearchResult]:
        logger.debug("Retrieving context for query (top_k=%d)", top_k)
        return await self._vector_store.similarity_search(query, top_k=top_k)
