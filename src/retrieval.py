from collections import defaultdict
from typing import Dict, List, Mapping, Optional, Tuple

import chromadb
from sentence_transformers import SentenceTransformer

from .bm25 import BM25Index, tokenize
from .config import Settings
from .models import Chunk, RetrievedChunk


def lexical_coverage(query: str, text: str) -> float:
    query_terms = set(tokenize(query))
    if not query_terms:
        return 0.0
    return len(query_terms.intersection(tokenize(text))) / len(query_terms)


class HybridRetriever:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        # Index creation performs the one-time download. Query-time loading is
        # offline-only so a running demo never depends on internet access.
        self.encoder = SentenceTransformer(settings.embedding_model, local_files_only=True)
        self.client = chromadb.PersistentClient(path=str(settings.chroma_dir))
        self.collection = self.client.get_collection(settings.collection_name)
        self.bm25 = BM25Index.load(settings.bm25_path)

    @staticmethod
    def _where(filters: Optional[Mapping[str, str]]) -> Optional[dict]:
        if not filters:
            return None
        clauses = [{key: value} for key, value in filters.items() if value not in (None, "")]
        if not clauses:
            return None
        return clauses[0] if len(clauses) == 1 else {"$and": clauses}

    def _validate_filters(self, filters: Optional[Mapping[str, str]]) -> Mapping[str, str]:
        normalized = dict(filters or {})
        unknown = set(normalized).difference(self.settings.allowed_filter_fields)
        if unknown:
            raise ValueError(f"Unsupported retrieval filters: {sorted(unknown)}")
        return {key: value for key, value in normalized.items() if value not in (None, "")}

    def retrieve(
        self,
        query: str,
        filters: Optional[Mapping[str, str]] = None,
        k: Optional[int] = None,
    ) -> List[RetrievedChunk]:
        if not query or not query.strip():
            raise ValueError("query must not be empty")
        k = self.settings.answer_top_k if k is None else k
        if k < 1:
            raise ValueError("k must be at least 1")
        filters = self._validate_filters(filters)
        candidate_k = max(
            self.settings.retrieval_candidates,
            k * self.settings.candidate_multiplier,
        )
        query_embedding = self.encoder.encode([query], normalize_embeddings=True)[0]
        vector = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=candidate_k,
            where=self._where(filters),
            include=["documents", "metadatas", "distances"],
        )
        bm25_results = self.bm25.search(query, candidate_k, filters)

        chunks: Dict[str, Chunk] = {}
        semantic_scores: Dict[str, float] = {}
        bm25_scores: Dict[str, float] = {}
        fused: Dict[str, float] = defaultdict(float)
        rrf_constant = self.settings.rrf_constant

        ids = vector.get("ids", [[]])[0]
        documents = vector.get("documents", [[]])[0]
        metadatas = vector.get("metadatas", [[]])[0]
        distances = vector.get("distances", [[]])[0]
        for rank, (chunk_id, text, metadata, distance) in enumerate(
            zip(ids, documents, metadatas, distances), start=1
        ):
            chunk = Chunk(chunk_id=chunk_id, text=text, **metadata)
            chunks[chunk_id] = chunk
            semantic_scores[chunk_id] = max(-1.0, 1.0 - float(distance))
            fused[chunk_id] += 1.0 / (rrf_constant + rank)

        for rank, (chunk, score) in enumerate(bm25_results, start=1):
            chunks[chunk.chunk_id] = chunk
            bm25_scores[chunk.chunk_id] = float(score)
            fused[chunk.chunk_id] += 1.0 / (rrf_constant + rank)

        ordered = sorted(fused, key=fused.get, reverse=True)[:k]
        return [
            RetrievedChunk(
                chunk=chunks[chunk_id],
                rank=rank,
                hybrid_score=fused[chunk_id],
                semantic_similarity=semantic_scores.get(chunk_id),
                bm25_score=bm25_scores.get(chunk_id),
            )
            for rank, chunk_id in enumerate(ordered, start=1)
        ]

    def has_sufficient_evidence(self, query: str, results: List[RetrievedChunk]) -> bool:
        if not results:
            return False
        best_semantic = max(
            (item.semantic_similarity for item in results if item.semantic_similarity is not None),
            default=-1.0,
        )
        best_coverage = max(lexical_coverage(query, item.chunk.text) for item in results)
        return (
            best_semantic >= self.settings.min_semantic_similarity
            and best_coverage >= self.settings.min_lexical_coverage
        )
