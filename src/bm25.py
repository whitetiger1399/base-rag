"""Small persistent BM25 implementation with no runtime service dependency."""

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .models import Chunk


TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)?")


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


class BM25Index:
    def __init__(
        self,
        chunks: Sequence[Chunk],
        term_frequencies: Sequence[Mapping[str, int]],
        document_frequencies: Mapping[str, int],
        lengths: Sequence[int],
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self.chunks = list(chunks)
        self.term_frequencies = [dict(item) for item in term_frequencies]
        self.document_frequencies = dict(document_frequencies)
        self.lengths = list(lengths)
        self.k1 = k1
        self.b = b
        self.average_length = sum(lengths) / max(1, len(lengths))

    @classmethod
    def build(
        cls, chunks: Sequence[Chunk], k1: float = 1.5, b: float = 0.75
    ) -> "BM25Index":
        term_frequencies: List[Dict[str, int]] = []
        document_frequencies: Counter = Counter()
        lengths: List[int] = []
        for chunk in chunks:
            frequencies = Counter(tokenize(chunk.text))
            term_frequencies.append(dict(frequencies))
            document_frequencies.update(frequencies.keys())
            lengths.append(sum(frequencies.values()))
        return cls(chunks, term_frequencies, document_frequencies, lengths, k1=k1, b=b)

    def score(self, query: str, index: int) -> float:
        query_terms = set(tokenize(query))
        tf = self.term_frequencies[index]
        length = self.lengths[index]
        total = len(self.chunks)
        score = 0.0
        for term in query_terms:
            frequency = tf.get(term, 0)
            if not frequency:
                continue
            df = self.document_frequencies.get(term, 0)
            idf = math.log(1.0 + (total - df + 0.5) / (df + 0.5))
            norm = frequency + self.k1 * (
                1.0 - self.b + self.b * length / max(self.average_length, 1.0)
            )
            score += idf * frequency * (self.k1 + 1.0) / norm
        return score

    def search(
        self,
        query: str,
        k: int,
        filters: Optional[Mapping[str, str]] = None,
    ) -> List[Tuple[Chunk, float]]:
        filters = filters or {}
        scored = []
        for index, chunk in enumerate(self.chunks):
            if any(str(getattr(chunk, key, "")) != str(value) for key, value in filters.items()):
                continue
            score = self.score(query, index)
            if score > 0:
                scored.append((chunk, score))
        return sorted(scored, key=lambda item: item[1], reverse=True)[:k]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "term_frequencies": self.term_frequencies,
            "document_frequencies": self.document_frequencies,
            "lengths": self.lengths,
            "k1": self.k1,
            "b": self.b,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "BM25Index":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            [Chunk.from_dict(item) for item in payload["chunks"]],
            payload["term_frequencies"],
            payload["document_frequencies"],
            payload["lengths"],
            payload["k1"],
            payload["b"],
        )
