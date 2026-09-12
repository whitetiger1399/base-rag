import argparse
from pathlib import Path

from src.chunking import chunk_documents, write_chunks
from src.config import SETTINGS


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Malawi IDSR Excel booklets")
    parser.add_argument("--data-dir", type=Path, default=SETTINGS.dataset_dir)
    parser.add_argument("--output", type=Path, default=SETTINGS.chunks_path)
    args = parser.parse_args()
    workbooks = sorted(args.data_dir.glob("*.xlsx"))
    if not workbooks:
        raise SystemExit(f"No .xlsx files found in {args.data_dir}")
    chunks = chunk_documents(
        workbooks,
        target_chars=SETTINGS.chunk_target_chars,
        max_chars=SETTINGS.chunk_max_chars,
    )
    count = write_chunks(chunks, args.output)
    print(f"Wrote {count} chunks from {len(workbooks)} workbooks to {args.output}")


if __name__ == "__main__":
    main()

