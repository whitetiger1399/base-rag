from src.evaluation import retrieval_metrics


def test_retrieval_metrics_distinguish_partial_and_full_evidence() -> None:
    items = [
        {"id": "a", "answerable": True, "relevant_chunk_ids": ["one", "two"]},
        {"id": "b", "answerable": True, "relevant_chunk_ids": ["three"]},
        {"id": "c", "answerable": False, "relevant_chunk_ids": []},
    ]
    metrics = retrieval_metrics(
        items,
        {"a": ["noise", "one"], "b": ["three"]},
        k=2,
    )
    assert metrics.evaluated_items == 2
    assert metrics.recall_at_k == 0.75
    assert metrics.hit_at_k == 1.0
    assert metrics.full_evidence_recall == 0.5
    assert metrics.mrr == 0.75
