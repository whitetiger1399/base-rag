from dataclasses import dataclass
from typing import List, Mapping, Optional

from .config import SETTINGS, Settings
from .generation import ABSTAIN_MESSAGE, generate_answer
from .models import RetrievedChunk
from .retrieval import HybridRetriever


@dataclass
class RAGResponse:
    answer: str
    retrieved: List[RetrievedChunk]
    abstained: bool


class MalawiRAG:
    def __init__(self, settings: Settings = SETTINGS) -> None:
        self.settings = settings
        self.retriever = HybridRetriever(settings)

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
        if not self.retriever.has_sufficient_evidence(query, results):
            return RAGResponse(ABSTAIN_MESSAGE, results, True)
        answer = generate_answer(query, results, self.settings)
        return RAGResponse(answer, results, answer == ABSTAIN_MESSAGE)

