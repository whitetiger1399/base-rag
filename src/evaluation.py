"""Reproducible retrieval metrics for the versioned Q3 golden set."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class RetrievalMetrics:
    recall_at_k: float
    hit_at_k: float
    full_evidence_recall: float
    mrr: float
    evaluated_items: int


def load_golden_set(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("golden set must contain a non-empty items list")
    return items


def retrieval_metrics(
    golden_items: Sequence[Mapping[str, object]],
    retrieved_ids: Mapping[str, Sequence[str]],
    k: int = 4,
) -> RetrievalMetrics:
    if k < 1:
        raise ValueError("k must be at least 1")
    recalls: list[float] = []
    hits: list[float] = []
    complete: list[float] = []
    reciprocal_ranks: list[float] = []
    for item in golden_items:
        if not item.get("answerable"):
            continue
        gold = {str(value) for value in item.get("relevant_chunk_ids", [])}
        if not gold:
            continue
        ranked = list(retrieved_ids.get(str(item["id"]), []))[:k]
        overlap = gold.intersection(ranked)
        recalls.append(len(overlap) / len(gold))
        hits.append(1.0 if overlap else 0.0)
        complete.append(1.0 if gold.issubset(ranked) else 0.0)
        reciprocal_ranks.append(
            next((1.0 / (rank + 1) for rank, value in enumerate(ranked) if value in gold), 0.0)
        )
    n = len(recalls)
    if not n:
        raise ValueError("no answerable golden items with gold chunks")
    return RetrievalMetrics(
        recall_at_k=sum(recalls) / n,
        hit_at_k=sum(hits) / n,
        full_evidence_recall=sum(complete) / n,
        mrr=sum(reciprocal_ranks) / n,
        evaluated_items=n,
    )
