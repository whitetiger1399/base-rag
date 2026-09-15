"""Apply or remove the standalone Q2 rag_reader filesystem policy."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DEFAULT_PATHS = [ROOT / "storage/chroma"]


def set_access(root: Path, locked: bool) -> int:
    if not root.is_dir():
        raise FileNotFoundError(root)
    paths = [root, *root.rglob("*")]
    paths = list(reversed(paths)) if locked else paths
    for path in paths:
        os.chmod(path, (0o555 if path.is_dir() else 0o444) if locked else
                       (0o755 if path.is_dir() else 0o644))
    return len(paths)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("lock", "unlock", "status"))
    parser.add_argument("paths", nargs="*", type=Path, default=DEFAULT_PATHS)
    args = parser.parse_args()
    for path in args.paths:
        path = path.resolve()
        if args.action == "status":
            from src.read_only_chroma import writable_paths
            writable = writable_paths(path)
            print(f"{path}: {'UNLOCKED' if writable else 'LOCKED'} ({len(writable)} writable paths)")
        else:
            count = set_access(path, locked=args.action == "lock")
            print(f"{path}: {args.action} applied to {count} paths")


if __name__ == "__main__":
    main()
