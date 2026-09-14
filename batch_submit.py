"""Generate SampleSubmission-format answers for Test.csv questions.

The answer is produced by the local MalawiRAG/Ollama pipeline. The remaining
submission fields are derived from retrieved evidence and the question so this
script does not require a second model call.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Iterable, List, Mapping

from src.config import SETTINGS
from src.rag import MalawiRAG


STOPWORDS = {
    "a", "an", "and", "are", "be", "by", "can", "do", "does", "for",
    "from", "how", "in", "is", "of", "on", "or", "should", "the", "to",
    "what", "when", "which", "why", "with", "during", "about", "this",
}
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'-]*")


def read_questions(path: Path, limit: int | None = None) -> List[Mapping[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or not {"ID", "Question Text"}.issubset(rows[0]):
        raise ValueError("test CSV must contain ID and Question Text columns")
    return rows if limit is None else rows[:limit]


def question_keywords(question: str, max_terms: int = 12) -> str:
    terms: List[str] = []
    for word in WORD_RE.findall(question):
        normalized = word.lower()
        if normalized in STOPWORDS or normalized in terms:
            continue
        terms.append(normalized)
    return ", ".join(terms[:max_terms])


def paragraph_numbers(response) -> str:
    ranges = []
    for item in response.retrieved:
        chunk = item.chunk
        value = str(chunk.paragraph_start)
        if chunk.paragraph_end != chunk.paragraph_start:
            value += f"-{chunk.paragraph_end}"
        if value not in ranges:
            ranges.append(value)
    return ", ".join(ranges)


def reference_documents(response) -> str:
    documents = []
    for item in response.retrieved:
        label = item.chunk.doc_id.replace("_", " ")
        if label not in documents:
            documents.append(label)
    return ", ".join(documents)


def submission_rows(
    questions: Iterable[Mapping[str, str]],
    rag: MalawiRAG,
    top_k: int | None,
    total: int,
):
    for number, row in enumerate(questions, start=1):
        question_id = row["ID"].strip()
        question = row["Question Text"].strip()
        percentage = number / total * 100 if total else 100
        print(
            f"\rProcessing test question {number}/{total} ({percentage:5.1f}%) — {question_id}",
            end="",
            flush=True,
        )
        response = rag.ask(question, k=top_k)
        values = {
            "keywords": question_keywords(question),
            "paragraph(s)_number": paragraph_numbers(response),
            "question_answer": response.answer,
            "reference_document": reference_documents(response),
        }
        for suffix in values:
            yield {"ID": f"{question_id}_{suffix}", "Target": values[suffix]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Test.csv through local Malawi RAG")
    parser.add_argument("--test-csv", type=Path, default=SETTINGS.dataset_dir.parent / "Test.csv")
    parser.add_argument("--output", type=Path, default=Path("shared_output/Q2_RAG_Demo/test_submission.csv"))
    parser.add_argument("--top-k", type=int, default=None)
    args = parser.parse_args()
    questions = read_questions(args.test_csv, SETTINGS.batch_max_questions)
    rag = MalawiRAG()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["ID", "Target"])
        writer.writeheader()
        writer.writerows(submission_rows(questions, rag, args.top_k, len(questions)))
    print()
    print(f"Wrote {len(questions)} questions ({len(questions) * 4} submission rows) to {args.output}")


if __name__ == "__main__":
    main()
