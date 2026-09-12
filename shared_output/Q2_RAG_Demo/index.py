import argparse
from pathlib import Path

from src.chunking import read_chunks
from src.config import SETTINGS
from src.indexing import build_index


def main() -> None:
    parser = argparse.ArgumentParser(description="Build vector and BM25 indexes")
    parser.add_argument("--chunks", type=Path, default=SETTINGS.chunks_path)
    args = parser.parse_args()
    if not args.chunks.exists():
        raise SystemExit(f"Missing {args.chunks}; run ingest.py first")
    count = build_index(read_chunks(args.chunks), SETTINGS)
    print(f"Indexed {count} chunks in Chroma and BM25")


if __name__ == "__main__":
    main()

