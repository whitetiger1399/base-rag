from pathlib import Path
from typing import List, Sequence

import chromadb
from sentence_transformers import SentenceTransformer

from .bm25 import BM25Index
from .config import Settings
from .models import Chunk


def _metadata(chunk: Chunk) -> dict:
    return {
        "doc_id": chunk.doc_id,
        "source_file": chunk.source_file,
        "section": chunk.section,
        "paragraph_start": chunk.paragraph_start,
        "paragraph_end": chunk.paragraph_end,
        "topic": chunk.topic,
    }


def build_index(chunks: Sequence[Chunk], settings: Settings) -> int:
    if not chunks:
        raise ValueError("Cannot build an index without chunks")

    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(settings.chroma_dir))
    try:
        client.delete_collection(settings.collection_name)
    except Exception:
        pass
    collection = client.create_collection(
        name=settings.collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    model = SentenceTransformer(settings.embedding_model, local_files_only=False)
    batch_size = 64
    for start in range(0, len(chunks), batch_size):
        batch = list(chunks[start : start + batch_size])
        embeddings = model.encode(
            [chunk.text for chunk in batch],
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        collection.add(
            ids=[chunk.chunk_id for chunk in batch],
            documents=[chunk.text for chunk in batch],
            metadatas=[_metadata(chunk) for chunk in batch],
            embeddings=embeddings.tolist(),
        )

    BM25Index.build(chunks).save(settings.bm25_path)
    return len(chunks)
