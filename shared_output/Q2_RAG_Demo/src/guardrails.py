"""Deterministic safety and citation checks shared by runtime and evaluations."""

import re
from typing import Iterable, List, Mapping, Sequence, Set

from .models import RetrievedChunk


ABSTAIN_MESSAGE = "cannot find in sources"
_INJECTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bignore\s+(?:all\s+)?(?:previous|prior|above|system)\s+instructions?\b",
        r"\b(?:override|bypass|disregard)\s+(?:the\s+)?(?:rules?|policy|guardrails?)\b",
        r"\b(?:reveal|print|repeat|expose)\s+(?:the\s+)?(?:system|developer)\s+prompt\b",
        r"\b(?:act|pretend)\s+as\s+(?:unrestricted|developer|admin)\b",
        r"\b(?:execute|run|call)\s+(?:this\s+)?(?:command|code|tool|function)\b",
    )
)
_BRACKET_RE = re.compile(r"\[([^\[\]]+)\]")


def detect_prompt_injection(text: str) -> bool:
    normalized = " ".join((text or "").split())
    return any(pattern.search(normalized) for pattern in _INJECTION_PATTERNS)


def source_ids(results: Iterable[RetrievedChunk]) -> Set[str]:
    return {item.chunk.chunk_id for item in results}


def extract_citations(answer: str) -> List[str]:
    return _BRACKET_RE.findall(answer or "")


def validate_citations(answer: str, allowed_ids: Iterable[str]) -> bool:
    citations = extract_citations(answer)
    return bool(citations) and set(citations).issubset(set(allowed_ids)) and all(
        citation in set(allowed_ids) for citation in citations
    )


def filter_untrusted_chunks(chunks: Sequence[Mapping[str, object]]) -> tuple[list[dict], list[str]]:
    safe: list[dict] = []
    quarantined: list[str] = []
    for raw in chunks:
        chunk = dict(raw)
        chunk_id = str(chunk.get("chunk_id", "unknown"))
        if detect_prompt_injection(str(chunk.get("text", ""))):
            quarantined.append(chunk_id)
        else:
            safe.append(chunk)
    return safe, quarantined
