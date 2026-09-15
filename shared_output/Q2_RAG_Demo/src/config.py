import os
import math
from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    dataset_dir: Path = PROJECT_ROOT / "Task2_dataset1" / "MWTGBookletsExcel"
    chunks_path: Path = PROJECT_ROOT / "storage" / "chunks.jsonl"
    chroma_dir: Path = PROJECT_ROOT / "storage" / "chroma"
    bm25_path: Path = PROJECT_ROOT / "storage" / "bm25" / "index.json"
    manifest_path: Path = PROJECT_ROOT / "storage" / "manifest.json"
    collection_name: str = "malawi_ids_guidelines"
    require_read_only_chroma: bool = True
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_local_files_only: bool = True
    ollama_model: str = "qwen3:8b"
    ollama_url: str = "http://127.0.0.1:11434"
    retrieval_candidates: int = 20
    answer_top_k: int = 6
    candidate_multiplier: int = 3
    rrf_constant: float = 60.0
    min_semantic_similarity: float = 0.28
    min_lexical_coverage: float = 0.12
    bm25_k1: float = 1.5
    bm25_b: float = 0.75
    chunk_target_chars: int = 1_800
    chunk_max_chars: int = 2_600
    chunk_overlap_paragraphs: int = 1
    max_context_chars: int = 8_000
    max_answer_tokens: int = 220
    request_timeout_seconds: float = 120.0
    generation_temperature: float = 0.1
    generation_context_tokens: int = 4_096
    index_batch_size: int = 64
    batch_max_questions: int = 50
    evaluation_max_questions: int = 10
    allowed_filter_fields: tuple[str, ...] = field(
        default=("doc_id", "source_file", "section", "topic")
    )

    def __post_init__(self) -> None:
        if self.answer_top_k < 1 or self.retrieval_candidates < 1:
            raise ValueError("retrieval counts must be positive")
        if self.candidate_multiplier < 1 or self.index_batch_size < 1 or self.batch_max_questions < 1 or self.evaluation_max_questions < 1:
            raise ValueError("candidate multiplier and index batch size must be positive")
        if not math.isfinite(self.rrf_constant) or self.rrf_constant <= 0:
            raise ValueError("rrf_constant must be a positive finite number")
        if not 0 <= self.min_semantic_similarity <= 1 or not 0 <= self.min_lexical_coverage <= 1:
            raise ValueError("evidence thresholds must be between 0 and 1")
        if not 0 < self.chunk_target_chars <= self.chunk_max_chars:
            raise ValueError("chunk_target_chars must be <= chunk_max_chars and positive")
        if self.chunk_overlap_paragraphs < 0:
            raise ValueError("chunk_overlap_paragraphs must be non-negative")
        if self.max_context_chars < 1 or self.max_answer_tokens < 1:
            raise ValueError("generation budgets must be positive")
        if not math.isfinite(self.request_timeout_seconds) or self.request_timeout_seconds <= 0 or self.generation_context_tokens < 1:
            raise ValueError("request timeout and context tokens must be positive")
        if not 0 <= self.generation_temperature <= 2:
            raise ValueError("generation_temperature must be between 0 and 2")
        if self.bm25_k1 < 0 or not 0 <= self.bm25_b <= 1:
            raise ValueError("invalid BM25 parameters")

    @classmethod
    def from_env(cls, **overrides: object) -> "Settings":
        """Apply explicit overrides over MALAWI_RAG_* environment values."""
        values = dict(overrides)
        fields = {
            "ollama_model": str, "ollama_url": str, "answer_top_k": int,
            "retrieval_candidates": int, "candidate_multiplier": int,
            "min_semantic_similarity": float, "min_lexical_coverage": float,
            "max_context_chars": int, "max_answer_tokens": int,
            "request_timeout_seconds": float, "generation_temperature": float,
            "generation_context_tokens": int, "evaluation_max_questions": int,
        }
        if "MALAWI_RAG_EMBEDDING_LOCAL_FILES_ONLY" in os.environ:
            values.setdefault(
                "embedding_local_files_only",
                os.environ["MALAWI_RAG_EMBEDDING_LOCAL_FILES_ONLY"].lower()
                in {"1", "true", "yes"},
            )
        for name, converter in fields.items():
            key = f"MALAWI_RAG_{name.upper()}"
            if key in os.environ and name not in values:
                values[name] = converter(os.environ[key])
        return cls(**values)

SETTINGS = Settings.from_env()
