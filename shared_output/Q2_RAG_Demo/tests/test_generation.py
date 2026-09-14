from src.config import Settings
from src.generation import _select_context, citations_are_valid, generate_answer
from src.models import Chunk, RetrievedChunk


def test_citation_validation_rejects_unknown_ids() -> None:
    chunk = Chunk("TG_Booklet_1:p1-p2:c0001", "text", "doc", "doc.xlsx", "section", 1, 2)
    result = RetrievedChunk(chunk, 1, 0.1)
    assert citations_are_valid("Claim [TG_Booklet_1:p1-p2:c0001]", [result])
    assert not citations_are_valid("Claim [TG_Booklet_2:p1-p2:c0001]", [result])
    assert not citations_are_valid("Claim without a source", [result])
    assert not citations_are_valid(
        "Claim [TG_Booklet_1:p1-p2:c0001] [invented]", [result]
    )


def test_context_allow_list_excludes_truncated_sources() -> None:
    first = RetrievedChunk(
        Chunk("one:p1-p1:c0001", "short", "doc", "doc.xlsx", "s", 1, 1), 1, 0.1
    )
    second = RetrievedChunk(
        Chunk("two:p2-p2:c0002", "also short", "doc", "doc.xlsx", "s", 2, 2), 2, 0.1
    )
    _, included = _select_context([first, second], max_chars=180)
    assert [item.chunk.chunk_id for item in included] == ["one:p1-p1:c0001"]


def test_settings_reject_invalid_generation_budget() -> None:
    try:
        Settings(max_answer_tokens=0)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid generation budget was accepted")


def test_settings_reject_invalid_rrf_constant() -> None:
    try:
        Settings(rrf_constant=0)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid RRF constant was accepted")


def test_generation_uses_configured_timeout(monkeypatch) -> None:
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": "Fact [one:p1-p1:c0001]"}}

    calls = []
    monkeypatch.setattr(
        "src.generation.requests.post",
        lambda *args, **kwargs: calls.append(kwargs) or Response(),
    )
    result = RetrievedChunk(
        Chunk("one:p1-p1:c0001", "evidence", "doc", "doc.xlsx", "s", 1, 1), 1, 0.1
    )
    generate_answer("question", [result], Settings(request_timeout_seconds=7))
    assert calls[0]["timeout"] == 7


def test_generation_rejects_mixed_fallback_answer(monkeypatch) -> None:
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": "Partial claim [one] cannot find in sources"}}

    monkeypatch.setattr("src.generation.requests.post", lambda *args, **kwargs: Response())
    result = RetrievedChunk(
        Chunk("one:p1-p1:c0001", "evidence", "doc", "doc.xlsx", "s", 1, 1), 1, 0.1
    )
    assert generate_answer("question", [result], Settings()) == "cannot find in sources"
