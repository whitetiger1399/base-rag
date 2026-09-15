# Read-only Chroma runtime policy

The RAG runtime treats the canonical Chroma index as a read-only artifact. Its
files use mode `0444` and directories use `0555`. At startup,
`ReadOnlyChromaStore` refuses an unlocked canonical directory, then copies the
index to a private temporary location. This copy is necessary because embedded
Chroma opens SQLite in writable mode even for queries. The retriever receives a
restricted interface exposing only `query()`; mutation methods raise
`PermissionError`. The disposable copy cannot persist changes to the canonical
index.

```text
canonical Chroma (0444/0555) -> private temporary copy -> query-only adapter -> RAG
```

The application never builds SQL from a question. Questions become embedding
vectors, filter keys pass an allow-list, and Chroma receives structured query
arguments. Prompt injection in source content remains covered by separate
guardrails.

## Service-principal boundary

This project uses `chromadb.PersistentClient`, an embedded local database. It
has no server-side users, service principals, grants, or read-only credentials.
An application token would not be enforced by Chroma and would create a false
security guarantee. The enforced local boundary is the operating-system account
and filesystem permissions, described as the `rag_reader` runtime role.

If a service principal is mandatory, deploy an authenticated Chroma server or
managed vector database with RBAC, create a server-side read-only identity,
store its secret outside Git, and use the authenticated network client. That is
a separate deployment architecture and is not claimed as implemented here.

## Commands

From the repository root:

```bash
rag-setup/bin/python scripts/chroma_access.py status
rag-setup/bin/python scripts/chroma_access.py lock
```

For an index rebuild, stop RAG processes and explicitly unlock, rebuild, and
relock:

```bash
rag-setup/bin/python scripts/chroma_access.py unlock
rag-setup/bin/python index.py
rag-setup/bin/python scripts/chroma_access.py lock
```

From the standalone Q2 folder use `python scripts/chroma_access.py ...`.

Git does not reliably preserve these read-only modes, so run `lock` after
cloning, copying, or rebuilding. Code executing as the file owner can
deliberately change modes; stronger isolation requires a separate OS account or
an authenticated server. This control protects the canonical index from
application and accidental writes, rather than sandboxing arbitrary owner code.
