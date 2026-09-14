"""Q4 graph-based multi-agent RAG reference implementation.

This dependency-free state machine shows the same nodes and conditional edges
that can be expressed in LangGraph. Retrieval, verification, and answering are
dependency injected so they can use the Q2 hybrid retriever and local Ollama.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence


ABSTAIN_MESSAGE = "cannot find in sources"
MAX_RETRIES = 2


class Route(str, Enum):
    SAFETY = "safety"
    VERIFY = "verify"
    RETRIEVE = "retrieve"
    ANSWER = "answer"
    ABSTAIN = "abstain"
    END = "end"


@dataclass
class GraphState:
    """Shared, serializable state passed between graph nodes."""

    original_query: str
    active_query: str = ""
    filters: Dict[str, str] = field(default_factory=dict)
    retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)
    safe_chunks: List[Dict[str, Any]] = field(default_factory=list)
    quarantined_ids: List[str] = field(default_factory=list)
    verifier_verdict: str = "pending"
    approved_ids: List[str] = field(default_factory=list)
    missing_facts: List[str] = field(default_factory=list)
    refined_query: str = ""
    retry_count: int = 0
    answer: str = ""
    cited_ids: List[str] = field(default_factory=list)
    abstain_reason: str = ""
    trace: List[Dict[str, Any]] = field(default_factory=list)
    max_retries: int = MAX_RETRIES

    def __post_init__(self) -> None:
        if not self.active_query:
            self.active_query = self.original_query


Retriever = Callable[[str, Mapping[str, str], int], Sequence[Mapping[str, Any]]]
Verifier = Callable[[str, Sequence[Mapping[str, Any]]], Mapping[str, Any]]
Answerer = Callable[[str, Sequence[Mapping[str, Any]]], str]


INJECTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bignore\s+(?:all\s+)?(?:previous|prior|above|system)\s+instructions?\b",
        r"\b(?:override|bypass|disregard)\s+(?:the\s+)?(?:rules?|policy|guardrails?)\b",
        r"\b(?:reveal|print|expose)\s+(?:the\s+)?(?:system|developer)\s+prompt\b",
        r"\bfollow\s+(?:only\s+)?(?:these|my)\s+instructions?\b",
        r"\b(?:execute|run|call)\s+(?:this\s+)?(?:command|code|tool|function)\b",
    )
)


def detect_prompt_injection(text: str) -> bool:
    normalized = " ".join((text or "").split())
    return any(pattern.search(normalized) for pattern in INJECTION_PATTERNS)


def retrieval_node(state: GraphState, retriever: Retriever, k: int = 4) -> GraphState:
    """Retrieve ranked candidates using the original or verifier-refined query."""
    state.retrieved_chunks = [
        dict(chunk) for chunk in retriever(state.active_query, state.filters, k)
    ]
    state.safe_chunks = []
    state.quarantined_ids = []
    state.trace.append(
        {
            "node": "retriever",
            "query": state.active_query,
            "result_ids": [c.get("chunk_id") for c in state.retrieved_chunks],
            "retry_count": state.retry_count,
        }
    )
    return state


def safety_node(state: GraphState) -> GraphState:
    """Quarantine retrieved chunks that contain prompt-injection indicators."""
    state.safe_chunks = []
    state.quarantined_ids = []
    for chunk in state.retrieved_chunks:
        chunk_id = str(chunk.get("chunk_id", "unknown"))
        if detect_prompt_injection(str(chunk.get("text", ""))):
            state.quarantined_ids.append(chunk_id)
        else:
            state.safe_chunks.append(chunk)
    state.trace.append(
        {
            "node": "safety",
            "safe_ids": [c.get("chunk_id") for c in state.safe_chunks],
            "quarantined_ids": list(state.quarantined_ids),
        }
    )
    return state


def verification_node(state: GraphState, verifier: Verifier) -> GraphState:
    """Decide whether safe evidence covers the question and suggest refinement."""
    if not state.safe_chunks:
        result: Mapping[str, Any] = {
            "verdict": "insufficient",
            "missing_facts": ["No safe evidence remained after filtering"],
            "refined_query": state.active_query,
        }
    else:
        result = verifier(state.original_query, state.safe_chunks)

    state.verifier_verdict = str(result.get("verdict", "insufficient"))
    state.approved_ids = [str(x) for x in result.get("approved_ids", [])]
    state.missing_facts = [str(x) for x in result.get("missing_facts", [])]
    state.refined_query = str(result.get("refined_query", "")).strip()
    state.trace.append(
        {
            "node": "verifier",
            "verdict": state.verifier_verdict,
            "approved_ids": list(state.approved_ids),
            "missing_facts": list(state.missing_facts),
        }
    )
    return state


def route_after_verification(state: GraphState, max_retries: int = MAX_RETRIES) -> Route:
    """Conditional edge leaving Verifier."""
    if max_retries < 0:
        state.abstain_reason = "invalid retry limit"
        return Route.ABSTAIN
    allowed = {str(c.get("chunk_id")) for c in state.safe_chunks}
    if (
        state.verifier_verdict == "sufficient"
        and state.approved_ids
        and set(state.approved_ids).issubset(allowed)
    ):
        return Route.ANSWER
    if state.verifier_verdict not in {"sufficient", "insufficient", "unsafe"}:
        state.abstain_reason = "malformed verifier verdict"
        return Route.ABSTAIN
    if state.verifier_verdict == "unsafe":
        state.abstain_reason = "unsafe request or evidence"
        return Route.ABSTAIN
    refined = state.refined_query.strip()
    if state.retry_count < max_retries and refined and refined != state.active_query:
        state.retry_count += 1
        state.active_query = refined
        return Route.RETRIEVE
    state.abstain_reason = "insufficient safe evidence after bounded retries"
    return Route.ABSTAIN


def answer_node(state: GraphState, answerer: Answerer) -> GraphState:
    """Generate only from verifier-approved chunks, then validate citations."""
    approved = [
        chunk
        for chunk in state.safe_chunks
        if str(chunk.get("chunk_id")) in set(state.approved_ids)
    ]
    candidate = answerer(state.original_query, approved).strip()
    found = re.findall(r"\[([^\[\]]+)\]", candidate)
    if not found or not set(found).issubset(set(state.approved_ids)):
        state.answer = ABSTAIN_MESSAGE
        state.abstain_reason = "answer contained missing or unapproved citations"
    else:
        state.answer = candidate
        state.cited_ids = found
    state.trace.append(
        {"node": "answerer", "cited_ids": list(state.cited_ids), "valid": bool(state.cited_ids)}
    )
    return state


# Assignment-facing aliases keep the graph contract readable in integrations.
retrieve_node = retrieval_node
verify_node = verification_node


def abstain_node(state: GraphState) -> GraphState:
    state.answer = ABSTAIN_MESSAGE
    state.cited_ids = []
    state.trace.append({"node": "abstain", "reason": state.abstain_reason})
    return state


def run_graph(
    query: str,
    retriever: Retriever,
    verifier: Verifier,
    answerer: Answerer,
    filters: Optional[Mapping[str, str]] = None,
    max_retries: int = MAX_RETRIES,
    k: int = 4,
) -> GraphState:
    """Execute graph edges until Answerer or Abstain reaches END."""
    if max_retries < 0 or k < 1:
        raise ValueError("max_retries must be non-negative and k must be positive")
    state = GraphState(original_query=query, filters=dict(filters or {}))
    state.max_retries = max_retries
    route = Route.RETRIEVE

    while route is not Route.END:
        if route is Route.RETRIEVE:
            retrieval_node(state, retriever, k=k)
            route = Route.SAFETY
        elif route is Route.SAFETY:
            safety_node(state)
            route = Route.VERIFY
        elif route is Route.VERIFY:
            verification_node(state, verifier)
            route = route_after_verification(state, max_retries)
        elif route is Route.ANSWER:
            answer_node(state, answerer)
            route = Route.END
        elif route is Route.ABSTAIN:
            abstain_node(state)
            route = Route.END
        else:
            raise RuntimeError(f"Unhandled graph route: {route}")

    return state
