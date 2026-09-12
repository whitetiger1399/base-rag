from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    dataset_dir: Path = PROJECT_ROOT / "Task2_dataset1" / "MWTGBookletsExcel"
    chunks_path: Path = PROJECT_ROOT / "storage" / "chunks.jsonl"
    chroma_dir: Path = PROJECT_ROOT / "storage" / "chroma"
    bm25_path: Path = PROJECT_ROOT / "storage" / "bm25" / "index.json"
    collection_name: str = "malawi_ids_guidelines"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ollama_model: str = "qwen3:8b"
    ollama_url: str = "http://127.0.0.1:11434"
    retrieval_candidates: int = 20
    answer_top_k: int = 4
    min_semantic_similarity: float = 0.28
    min_lexical_coverage: float = 0.12
    chunk_target_chars: int = 1_800
    chunk_max_chars: int = 2_600
    max_context_chars: int = 8_000
    max_answer_tokens: int = 220


SETTINGS = Settings()
