"""Q1 required snippets, backed by the working Q2 implementation."""

from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

from src.chunking import chunk_documents as _chunk_documents
from src.config import SETTINGS
from src.indexing import build_index as _build_index
from src.models import Chunk, RetrievedChunk
from src.retrieval import HybridRetriever


_db: Optional[HybridRetriever] = None


def chunk_documents(docs: Iterable[Path]) -> list[Chunk]:
    """Create section-aware chunks with stable booklet/paragraph metadata."""
    return _chunk_documents(
        docs,
        target_chars=SETTINGS.chunk_target_chars,
        max_chars=SETTINGS.chunk_max_chars,
        overlap_paragraphs=SETTINGS.chunk_overlap_paragraphs,
    )


def build_index(chunks: Sequence[Chunk]) -> HybridRetriever:
    """Build persistent cosine-vector and BM25 indexes over identical chunks."""
    global _db
    _build_index(chunks, SETTINGS)
    _db = HybridRetriever(SETTINGS)
    return _db


def retrieve(
    query: str,
    filters: Optional[Mapping[str, str]],
    k: int,
) -> list[RetrievedChunk]:
    """Return the top hybrid results after metadata filtering and RRF fusion."""
    global _db
    if _db is None:
        _db = HybridRetriever(SETTINGS)
    return _db.retrieve(query=query, filters=filters, k=k)
