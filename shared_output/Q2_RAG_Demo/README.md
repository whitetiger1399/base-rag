# Malawi Public Health RAG

This project builds a local retrieval-augmented assistant over the Malawi
Integrated Disease Surveillance and Response (IDSR) training-guide workbooks.
It uses structure-aware chunks, a local sentence-transformer embedding index,
BM25 retrieval, reciprocal-rank fusion, and Ollama `qwen3:8b` generation.

## Features

- Excel ingestion that preserves booklet, section, and paragraph metadata
- Persistent Chroma cosine index plus persistent BM25 index
- Hybrid retrieval with stable chunk IDs
- Mandatory inline citations to retrieved chunks
- Exact `cannot find in sources` abstention behavior
- Streamlit interface and command-line interface
- Trace mode with rank, semantic similarity, BM25 score, and source text
- Validated configuration with `MALAWI_RAG_*` environment overrides
- Versioned golden set and retrieval metrics under the Q3 deliverable

## Setup

Use Python 3.9. The development repository already has a virtual environment
named `rag-setup`; create it first when running a shared standalone copy.

```bash
python3.9 -m venv rag-setup
source rag-setup/bin/activate
python -m pip install -r requirements-lock.txt
ollama run qwen3:8b
```

Use `requirements.txt` when resolving compatible dependency updates; use
`requirements-lock.txt` for the tested Python 3.9 environment.

The embedding model is downloaded once by `sentence-transformers`, then runs
locally. Ollama must be running at `http://127.0.0.1:11434`.
Indexing uses the cached local model by default; set
`MALAWI_RAG_EMBEDDING_LOCAL_FILES_ONLY=false` for the first model download.

Selected settings can be overridden without editing source, for example:

```bash
export MALAWI_RAG_ANSWER_TOP_K=6
export MALAWI_RAG_MAX_ANSWER_TOKENS=360
```

## Build the indexes

```bash
python ingest.py
python index.py
```

By default, ingestion reads `Task2_dataset1/MWTGBookletsExcel/*.xlsx` and writes
generated indexes under `storage/`.

The source dataset and generated indexes are included in this repository for a
reproducible assignment review. Rebuild them after changing chunking or model
settings; `storage/manifest.json` records the corpus and index parameters.

## Run

```bash
streamlit run app.py
```

## Batch test submission

Run a parameterized prefix of `Test.csv` and write rows matching
`SampleSubmission.csv` (`ID`, `Target`):

```bash
python batch_submit.py
```

The script generates the answer with local Ollama `qwen3:8b`, derives keywords
from the question, and derives paragraph/document fields from retrieved chunks.
It processes the number configured by `Settings.batch_max_questions` (10 by
default) and creates a timestamped `test_submission_YYYY_MM_DD_HH_MM_SS.csv`
file. `--top-k`, `--test-csv`, and `--output` remain configurable.
Each completed test question is flushed to the CSV immediately, so partial
results remain available while a longer run is still processing.

For a visual explanation of the complete ingestion, indexing, retrieval, Ollama,
and citation flow, see `docs/RAG_FLOW_EXPLAINED.pdf`.

For a CLI query with retrieval evidence:

```bash
python rag.py "What is community-based surveillance?" --trace
```

## Answer policy

Retrieved workbook content is treated as untrusted reference data. The model is
instructed to ignore instructions inside sources, answer only from the supplied
evidence, and cite stable chunk IDs. Answers without valid retrieved citations
are replaced with `cannot find in sources`. The interface provides general
public-health information and does not give personal medical advice.
