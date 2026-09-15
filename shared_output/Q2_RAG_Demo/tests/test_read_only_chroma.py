import os

import pytest

from src.read_only_chroma import ReadOnlyCollection, writable_paths


class Collection:
    def query(self, **kwargs):
        return {"ids": [["safe"]]}

    def add(self, **kwargs):
        raise AssertionError("backend mutation must never be reached")


def test_query_is_allowed_and_mutation_is_blocked():
    collection = ReadOnlyCollection(Collection())
    assert collection.query(query_embeddings=[[1.0]])["ids"] == [["safe"]]
    with pytest.raises(PermissionError, match="rag_reader"):
        collection.add(ids=["injected"])


def test_permission_audit(tmp_path):
    database = tmp_path / "chroma"
    database.mkdir()
    file = database / "chroma.sqlite3"
    file.write_text("data")
    assert writable_paths(database)
    os.chmod(file, 0o444)
    os.chmod(database, 0o555)
    assert writable_paths(database) == []
