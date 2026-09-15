"""Read-only runtime access to a local embedded Chroma index."""

from __future__ import annotations

import atexit
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import chromadb


MUTATING_METHODS = {
    "add", "delete", "modify", "update", "upsert",
    "create_collection", "delete_collection", "get_or_create_collection", "reset",
}


def writable_paths(root: Path) -> list[Path]:
    if not root.is_dir():
        raise FileNotFoundError(f"Missing Chroma index directory: {root}")
    return [path for path in [root, *root.rglob("*")] if path.stat().st_mode & 0o222]


class ReadOnlyCollection:
    __slots__ = ("__collection",)

    def __init__(self, collection: Any) -> None:
        self.__collection = collection

    def query(self, **kwargs: Any) -> dict:
        return self.__collection.query(**kwargs)

    def __getattr__(self, name: str) -> Any:
        if name in MUTATING_METHODS:
            raise PermissionError(f"Chroma runtime role 'rag_reader' cannot call {name}()")
        raise AttributeError(f"Read-only Chroma collection does not expose {name!r}")


class ReadOnlyChromaStore:
    """Query a private snapshot while leaving the canonical index read-only."""

    def __init__(self, source: Path, collection_name: str, require_locked: bool = True) -> None:
        source = source.resolve()
        if require_locked:
            writable = writable_paths(source)
            if writable:
                raise PermissionError(
                    "Canonical Chroma index is writable. Apply the rag_reader filesystem policy first."
                )
        self._temporary = tempfile.TemporaryDirectory(prefix="malawi-rag-chroma-")
        atexit.register(self.close)
        runtime_path = Path(self._temporary.name) / "chroma"
        shutil.copytree(source, runtime_path)
        for path in [runtime_path, *runtime_path.rglob("*")]:
            os.chmod(path, 0o700 if path.is_dir() else 0o600)
        self._client = chromadb.PersistentClient(path=str(runtime_path))
        self.collection = ReadOnlyCollection(self._client.get_collection(collection_name))

    def close(self) -> None:
        temporary = getattr(self, "_temporary", None)
        if temporary is not None:
            temporary.cleanup()
            self._temporary = None
