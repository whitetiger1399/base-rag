from src.bm25 import BM25Index
from src.models import Chunk


def make_chunk(chunk_id: str, text: str) -> Chunk:
    return Chunk(chunk_id, text, "doc", "doc.xlsx", "section", 1, 1)


def test_bm25_ranks_matching_chunk_first() -> None:
    chunks = [
        make_chunk("one", "cholera case definition and surveillance"),
        make_chunk("two", "routine administrative meeting"),
    ]
    results = BM25Index.build(chunks).search("cholera surveillance", k=2)
    assert results[0][0].chunk_id == "one"

