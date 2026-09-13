import argparse

from src.rag import MalawiRAG


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the local Malawi RAG assistant")
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=None)
    parser.add_argument("--trace", action="store_true")
    args = parser.parse_args()
    response = MalawiRAG().ask(args.query, k=args.top_k)
    print(response.answer)
    if args.trace:
        print("\nRetrieved evidence:")
        for item in response.retrieved:
            semantic = "n/a" if item.semantic_similarity is None else f"{item.semantic_similarity:.3f}"
            bm25 = "n/a" if item.bm25_score is None else f"{item.bm25_score:.3f}"
            print(
                f"{item.rank}. [{item.chunk.chunk_id}] semantic={semantic} "
                f"bm25={bm25} hybrid={item.hybrid_score:.5f} section={item.chunk.section}"
            )
            print(item.chunk.text)


if __name__ == "__main__":
    main()
