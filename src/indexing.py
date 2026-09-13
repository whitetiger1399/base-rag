import hashlib
import json
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
    # The model is resolved during environment setup; index builds remain
    # deterministic and offline once that local artifact is available.
    model = SentenceTransformer(
        settings.embedding_model,
        local_files_only=settings.embedding_local_files_only,
    )
    embeddings_by_batch = []
    for start in range(0, len(chunks), settings.index_batch_size):
        batch = list(chunks[start : start + settings.index_batch_size])
        embeddings_by_batch.append(
            model.encode(
                [chunk.text for chunk in batch],
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        )
    client = chromadb.PersistentClient(path=str(settings.chroma_dir))
    try:
        client.delete_collection(settings.collection_name)
    except ValueError:
        pass
    collection = client.create_collection(
        name=settings.collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    for batch_number, start in enumerate(
        range(0, len(chunks), settings.index_batch_size)
    ):
        batch = list(chunks[start : start + settings.index_batch_size])
        embeddings = embeddings_by_batch[batch_number]
        collection.add(
            ids=[chunk.chunk_id for chunk in batch],
            documents=[chunk.text for chunk in batch],
            metadatas=[_metadata(chunk) for chunk in batch],
            embeddings=embeddings.tolist(),
        )

    BM25Index.build(chunks, k1=settings.bm25_k1, b=settings.bm25_b).save(settings.bm25_path)
    digest = hashlib.sha256(
        "\n".join(chunk.chunk_id for chunk in chunks).encode("utf-8")
    ).hexdigest()
    settings.manifest_path.parent.mkdir(parents=True, exist_ok=True)
    settings.manifest_path.write_text(
        json.dumps(
            {
                "chunk_count": len(chunks),
                "chunk_id_sha256": digest,
                "embedding_model": settings.embedding_model,
                "collection_name": settings.collection_name,
                "rrf_constant": settings.rrf_constant,
                "bm25_k1": settings.bm25_k1,
                "bm25_b": settings.bm25_b,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return len(chunks)
