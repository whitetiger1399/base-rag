from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    doc_id: str
    source_file: str
    section: str
    paragraph_start: int
    paragraph_end: int
    topic: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "Chunk":
        return cls(**value)


@dataclass
class RetrievedChunk:
    chunk: Chunk
    rank: int
    hybrid_score: float
    semantic_similarity: Optional[float] = None
    bm25_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        result = self.chunk.to_dict()
        result.update(
            rank=self.rank,
            hybrid_score=self.hybrid_score,
            semantic_similarity=self.semantic_similarity,
            bm25_score=self.bm25_score,
        )
        return result

