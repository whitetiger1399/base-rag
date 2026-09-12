from src.generation import citations_are_valid
from src.models import Chunk, RetrievedChunk


def test_citation_validation_rejects_unknown_ids() -> None:
    chunk = Chunk("TG_Booklet_1:p1-p2:c0001", "text", "doc", "doc.xlsx", "section", 1, 2)
    result = RetrievedChunk(chunk, 1, 0.1)
    assert citations_are_valid("Claim [TG_Booklet_1:p1-p2:c0001]", [result])
    assert not citations_are_valid("Claim [TG_Booklet_2:p1-p2:c0001]", [result])
    assert not citations_are_valid("Claim without a source", [result])

