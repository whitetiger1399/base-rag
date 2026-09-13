from dataclasses import dataclass, field
from typing import Callable, List, Mapping, Optional

from .config import SETTINGS, Settings
from .generation import ABSTAIN_MESSAGE, generate_answer
from .guardrails import detect_prompt_injection
from .models import RetrievedChunk
from .retrieval import HybridRetriever


@dataclass
class RAGResponse:
    answer: str
    retrieved: List[RetrievedChunk]
    abstained: bool
    quarantined_ids: List[str] = field(default_factory=list)


class MalawiRAG:
    def __init__(
        self,
        settings: Settings = SETTINGS,
        retriever: Optional[HybridRetriever] = None,
        answer_generator: Callable = generate_answer,
    ) -> None:
        self.settings = settings
        self.retriever = retriever or HybridRetriever(settings)
        self.answer_generator = answer_generator

    def ask(
        self,
        query: str,
        filters: Optional[Mapping[str, str]] = None,
        k: Optional[int] = None,
    ) -> RAGResponse:
        query = query.strip()
        if not query:
            return RAGResponse(ABSTAIN_MESSAGE, [], True)
        results = self.retriever.retrieve(query, filters=filters, k=k)
        safe_results = []
        quarantined_ids = []
        for result in results:
            if detect_prompt_injection(result.chunk.text):
                quarantined_ids.append(result.chunk.chunk_id)
            else:
                safe_results.append(result)
        if not self.retriever.has_sufficient_evidence(query, safe_results):
            return RAGResponse(ABSTAIN_MESSAGE, results, True, quarantined_ids)
        answer = self.answer_generator(query, safe_results, self.settings)
        return RAGResponse(answer, results, answer == ABSTAIN_MESSAGE, quarantined_ids)
