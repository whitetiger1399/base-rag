# Malawi RAG — Project Record and Agent Instructions

Created: 2026-09-10

This document records the user's requests, assignment requirements, decisions,
planned work, and completed work. Paths below are relative to the `malawi-rag/`
project root unless stated otherwise. Its location is `rag-setup/docs/AGENTS.md`,
as requested by the user.

## 1. How to Maintain This File

- Append dated entries inside the relevant section; do not replace the whole file.
- Preserve earlier requests, decisions, and progress entries as history.
- When a decision changes, append a correction identifying the earlier decision
  and explaining what supersedes it. Do not silently delete the earlier entry.
- Use these labels: **User request**, **Confirmed**, **User-reported**,
  **Proposed**, **Pending**, **Completed**, and **Superseded**.
- Distinguish plans from implementation and user-reported setup from tested setup.
- After meaningful work, append its outcome, affected paths, and validation to
  the appropriate sections and add a short activity-log entry.
- Add new sections when needed, preserving existing sections and their history.
- Record actual results only. Do not mark planned deliverables or unrun tests as complete.

Suggested entry format:

```markdown
### YYYY-MM-DD — Short update title

- **Status:** User request / Confirmed / User-reported / Proposed / Pending / Completed / Superseded
- **Details:** What was requested, decided, or changed.
- **Evidence / files:** Relevant paths or checks, when applicable.
- **Next action:** Remaining work, when applicable.
```

## 2. Problem Statement

### 2026-09-10 — Assignment context

- **Confirmed:** The assignment concerns a RAG assistant over a Malawi public
  health dataset, using a local LLM only.
- The system must retrieve relevant evidence, answer with citations, abstain
  when sources are insufficient, and expose retrieved evidence through trace mode.
- The assignment also requires retrieval design, guardrails and evaluation,
  a multi-agent workflow plan, and a graph-based workflow with bounded retries.
- **Source:** `Assigment_questions.docx`, read in this session without edits.
- The requirements recorded here are a project reference, not completed assignment answers.

## 3. User Requests and Working Boundaries

### 2026-09-12 — Repository publication request

- **User request:** Push the current project code to
  `https://github.com/whitetiger1399/base-rag.git`.
- **Confirmed:** The target repository was checked with `git ls-remote` and was
  empty before the first push.
- **Planned:** Initialize this workspace as a Git repository, create the first
  commit on `main`, and push it to the requested `origin`.

### 2026-09-10 — Requests received

1. Read `Assigment_questions.docx` only; do not start summarization at that stage.
2. Read `requirements-lock.txt` and note the new `rag-setup` environment.
3. Note that the user ran `ollama run qwen3:8b` and reported it running.
4. Organize all shareable assignment results under `shared_output/`, including
   PDFs, documents, and separate Python or pseudocode files.
5. Refine that structure to use one subdirectory per assignment, containing
   all corresponding deliverables and outputs.
6. Create a structured agent Markdown record in the `rag-setup` docs section,
   capturing the problem, requests, plans, and progress.
7. Maintain this record by appending within sections, without overwriting it completely.

### 2026-09-10 — Current scope

- **Confirmed:** Current work is setup organization and project documentation.
- **Pending:** Assignment implementation and final deliverable generation have
  not started in this conversation.
- Future plans below describe intended project work; they do not claim that it
  has already been implemented or tested.

## 4. Environment and Inputs

### 2026-09-12 — Q2 environment validation

- **Completed:** Verified `rag-setup` uses Python 3.9.12.
- **Completed:** Installed the minimal Q2 dependencies into `rag-setup`.
- **Confirmed:** The original `requirements-lock.txt` pin `torch==2.6.0` is not
  compatible with this Python 3.9 Intel macOS runtime. The Q2 requirements use
  `torch==2.2.2` and `numpy==1.26.4`; the original lock file was preserved.
- **Completed:** Downloaded `sentence-transformers/all-MiniLM-L6-v2` for local
  embeddings and configured query-time loading as offline-only.
- **Completed:** Verified Ollama reports `qwen3:8b` installed and loaded on GPU.
- **Completed:** Verified a minimal Ollama chat request returned HTTP 200 and `OK`.

### 2026-09-10 — Known setup

| Item | Status | Details |
| --- | --- | --- |
| Project | Confirmed | `malawi-rag/` is the working project root. |
| Assignment document | Completed | `Assigment_questions.docx` has been read. |
| Dependency lock file | Completed | `requirements-lock.txt` has been read; installation and compatibility have not been validated. |
| Python environment | User-reported; directory observed | Environment is named `rag-setup`; the directory contains `bin/`, `lib/`, and `pyvenv.cfg`. |
| Local model | User-reported | User ran `ollama run qwen3:8b`; service availability and inference have not been independently tested. |
| Dataset directory | Observed | `Task2_dataset1/MWTGBookletsExcel/` contains Excel booklets; their contents have not been reviewed. |

The lock file includes packages for local inference, embeddings, retrieval,
application interfaces, and tracking, including Ollama, Transformers,
sentence-transformers, ChromaDB, bm25s, LangChain, LlamaIndex, Streamlit, and MLflow.
Their presence in the file does not mean they are installed in `rag-setup` or
that all will be used.

## 5. Assignment Requirements

### 2026-09-10 — Q1: Retrieval Design

- Write a 1–2 page retrieval design focused on answer correctness.
- Cover structure-aware chunking for headings, lists, small sections, and long sections.
- Describe indexing and metadata, such as document ID, section, and topic.
- Compare vector-only retrieval with hybrid BM25 and vector retrieval; explain `top_k` selection.
- Describe local reranking: cross-encoder, lexical/vector fusion, or local LLM reranking.
- Include short pseudocode or real-code snippets for:
  - `chunk_documents(docs) -> chunks`
  - `build_index(chunks) -> db`
  - `retrieve(query, filters, k) -> top_chunks`
- Required deliverables: `Q1_Retrieval_Design.pdf` and `snippets_q1.py`.

### 2026-09-10 — Q2: Working Local RAG Demo

- Implement ingestion, chunking, embeddings, and an index.
- Provide a CLI, Streamlit, or Gradio query interface.
- Cite chunk IDs or section names in answers.
- Say “cannot find in sources” when evidence is insufficient.
- Provide trace mode showing retrieved chunks and similarity scores or ranks.
- Provide 10 demo questions with actual outputs, including at least two correct
  abstentions and at least two answers citing multiple chunks.
- Deliver a runnable repository or zipped folder with `README.md`, `ingest.py`,
  `index.py`, `rag.py`, `app.py`, and `demo_outputs.md`.
- Include a short video or screenshots showing the demo running.
- Required deliverable folder: `Q2_RAG_Demo/`.

### 2026-09-10 — Q3: Guardrails, Evaluation, and Multi-Agent Plan

- Describe prompt-injection defense for untrusted retrieved text.
- Require citations and prevent guessing; use a public-health-information tone
  rather than personal medical advice.
- Plan a golden set of 15–20 questions, Recall@k and MRR measurement, and
  grounding/faithfulness checks.
- Design Retriever → Verifier → Answerer, with an optional Safety agent;
  specify each agent's responsibilities and outputs.
- Explain use of MLflow in the multi-agent workflow.
- Include `detect_prompt_injection(text) -> bool`,
  `faithfulness_check(answer, cited_chunks) -> score`, and minimal orchestration snippets.
- Required deliverables: `Q3_Guardrails_Eval_Agents.pdf` and `snippets_q3.py`.

### 2026-09-10 — Q4: Graph-Based Multi-Agent RAG

- Design graph state, nodes, node outputs, and conditional transitions for
  Retriever → Verifier → Answerer, with an optional Safety node.
- Route insufficient evidence back to retrieval using a refined query.
- Filter detected prompt-injection chunks and re-verify.
- Define stopping conditions, bounded retries (assignment example: two), and
  an abstention path when evidence remains insufficient.
- Include a TypedDict/dataclass state, retrieval/verification/answer node
  functions, optional safety node, and conditional routing snippets.
- Required deliverables: `graph-based-multi-agent.pdf` and `snippets_q4.py`.

## 6. Folder Structure and Sharing Decisions

### 2026-09-10 — Working project layout

**Proposed:** The user supplied the following development layout. Except for
the confirmed items recorded in the progress section, this is a plan, not a
claim that the files exist.

```text
malawi-rag/
├── data/raw/
├── storage/
│   ├── chroma/
│   └── bm25/
├── src/
│   ├── chunking.py
│   ├── indexing.py
│   ├── retrieval.py
│   ├── reranking.py
│   ├── guardrails.py
│   ├── generation.py
│   ├── graph.py
│   └── evaluation.py
├── tests/
├── rag-setup/
│   └── docs/AGENTS.md
├── shared_output/
├── app.py
├── requirements.txt
├── requirements-lock.txt
└── README.md
```

### 2026-09-10 — Per-assignment submission layout

**Confirmed user preference:** Group all shareable files by assignment.
Keep code/pseudocode in separate files alongside that assignment's documents.
The four assignment directories exist; the contents below are planned.

```text
shared_output/
├── Q1_Retrieval_Design/
│   ├── Q1_Retrieval_Design.pdf
│   ├── Q1_Retrieval_Design.docx
│   └── snippets_q1.py
├── Q2_RAG_Demo/
│   ├── README.md
│   ├── requirements.txt
│   ├── requirements-lock.txt
│   ├── ingest.py
│   ├── index.py
│   ├── rag.py
│   ├── app.py
│   ├── src/
│   ├── demo_outputs.md
│   └── screenshots/
├── Q3_Guardrails_Eval_Agents/
│   ├── Q3_Guardrails_Eval_Agents.pdf
│   ├── Q3_Guardrails_Eval_Agents.docx
│   └── snippets_q3.py
└── Q4_Graph_Multi_Agent/
    ├── graph-based-multi-agent.pdf
    ├── graph-based-multi-agent.docx
    └── snippets_q4.py
```

- **Proposed:** Use editable `.docx` companions for the written PDFs, reflecting
  the user's request to include documents as well as PDFs.
- **Proposed:** Package Q2 as a standalone runnable copy with its dependencies,
  source files, and dataset setup instructions.
- Put additional task-specific results in that task's folder.
- **Superseded:** The earlier suggestion of shared `pdfs/` and `snippets/`
  directories is replaced by the user's per-assignment organization.
- **Superseded:** Assignment delivery folders at project root are replaced by
  the corresponding folders under `shared_output/`.

## 7. Planned Work

### 2026-09-12 — Q2 design selected

- **Confirmed:** Use workbook paragraph numbers as stable citation boundaries.
- **Confirmed:** Use structure-aware chunks with heading metadata and sentence
  splitting for oversized spreadsheet cells.
- **Confirmed:** Use normalized MiniLM embeddings in Chroma plus a persistent
  local BM25 index, combined with reciprocal-rank fusion.
- **Confirmed:** Use local Ollama `qwen3:8b` for answer generation and Streamlit
  for the interactive interface.
- **Confirmed:** Require exact bracketed chunk citations, apply a semantic and
  lexical evidence gate, and return `cannot find in sources` on insufficient
  evidence or invalid citations.
- **Pending:** Calibrate retrieval and abstention thresholds using a golden set.
- **Pending:** Capture eight more demo outputs, including a second abstention and
  at least two multi-chunk-citation answers, then capture final screenshots.

### 2026-09-10 — Implementation sequence for future work

1. Inspect the dataset's actual structure and verify the environment and local model.
2. Select structure-aware chunking, metadata, embedding, retrieval, and local
   reranking approaches based on the data and runtime constraints.
3. Implement ingestion and indexing, then retrieval, generation, citations,
   abstention, and trace mode.
4. Build a query interface and capture the required Q2 demo outputs and visual evidence.
5. Develop guardrail and evaluation designs, a golden set, and MLflow tracking design.
6. Define the graph workflow with verification, refinement, filtering, retry
   limits, and abstention.
7. Write the Q1, Q3, and Q4 documents and corresponding snippets, ensuring
   descriptions agree with actual implementation where applicable.
8. Validate and package each assignment in its `shared_output/` directory.

**Pending decisions:** Exact embedding model, chunk sizes, metadata schema,
retrieval parameters, reranker, interface, and graph framework remain undecided.
Chroma/BM25 appear in the proposed layout; they have not been implemented.

## 8. Progress and Validation

### 2026-09-12 — Q2 implementation started

| Work item | Status | Evidence / limitation |
| --- | --- | --- |
| Inspect dataset | Completed | Six workbook schemas inspected; column A is paragraph number and column B is source text. |
| Structure-aware ingestion | Completed | 787 chunks generated from six workbooks. |
| Chunk quality check | Completed | Lengths: 56 min, 1,593 average, 2,663 max including section context; only three chunks under 100 characters. |
| Vector index | Completed | Chroma cosine index built using local `all-MiniLM-L6-v2`. |
| Lexical index | Completed | Persistent BM25 index built over the same chunks. |
| Hybrid retrieval | Completed | Reciprocal-rank fusion implemented and verified on a CBS query. |
| Citation controls | Completed | Stable chunk citations and deterministic allow-list validation implemented. |
| Abstention | Completed | Out-of-domain Formula One engine-oil query returned exact `cannot find in sources`. |
| Ollama generation | Completed | CBS query produced a grounded answer citing `TG_Booklet_1:p430-p436:c0066`. |
| Streamlit setup | Completed | Server launched on port 8501 and returned HTTP 200; visual browser automation was unavailable in this tool session. |
| Automated tests | Completed | Six tests pass in both the development root and packaged Q2 copy. |
| Q2 package | In progress | Runnable package created in `shared_output/Q2_RAG_Demo/`; final demo set and screenshots remain. |

Implemented development paths:

- `src/chunking.py`, `src/bm25.py`, `src/indexing.py`, `src/retrieval.py`
- `src/generation.py`, `src/rag.py`, `src/config.py`, `src/models.py`
- `ingest.py`, `index.py`, `rag.py`, `app.py`
- `tests/`, `docs/Q2_DESIGN.md`, `demo_outputs.md`, `README.md`
- Generated `storage/chunks.jsonl`, `storage/chroma/`, and `storage/bm25/`

Packaged deliverable path: `shared_output/Q2_RAG_Demo/`.

### 2026-09-10 — Initial progress record

| Work item | Status | Evidence / limitation |
| --- | --- | --- |
| Read assignment | Completed | Text read from `Assigment_questions.docx`; no edits. |
| Read dependencies | Completed | `requirements-lock.txt` read; no packages installed by the assistant. |
| Record environment | Completed | User's `rag-setup` name recorded; environment directory observed. |
| Record local model | Completed | User's Ollama report recorded; no inference check performed. |
| Create assignment folders | Completed | Four task directories under `shared_output/` created and observed. |
| Create project record | Completed | This file created at the user's requested docs location. |
| Inspect dataset contents | Pending | File names observed only. |
| Implement and test RAG | Pending | No implementation or tests performed in this session. |
| Generate submission files | Pending | PDFs, DOCX files, snippets, and demo evidence have not been generated. |

## 9. Open Questions and Follow-Up Checks

### 2026-09-12 — Q2 remaining validation

- Tune evidence thresholds against labeled Train.csv references rather than
  relying only on initial engineering defaults.
- Complete all ten required demo questions and outputs.
- Ensure at least two final outputs abstain and at least two cite multiple chunks.
- Capture Streamlit screenshots after the final UI and demo questions stabilize.
- Consider reducing generation latency; the first grounded `qwen3:8b` RAG answer
  took about 90 seconds with three evidence chunks on the current machine.

### 2026-09-10 — Items to resolve during implementation

- Verify Python version and dependency compatibility before choosing runtime details.
- Check which locked dependencies are actually installed in `rag-setup`.
- Verify Ollama availability and `qwen3:8b` inference when implementation begins.
- Inspect the dataset before deciding how to preserve headings, tables, lists,
  section names, and source identifiers.
- Decide whether the Q2 package bundles the dataset or documents how to obtain it.
- Select retrieval and abstention parameters using evidence from evaluation.

## 10. Activity Log

### 2026-09-12 — GitHub publication preparation

- Confirmed the workspace was not previously a Git repository.
- Confirmed the requested GitHub repository had no existing refs.
- Updated `.gitignore` to exclude the 1.6 GB virtual environment while retaining
  `rag-setup/docs/AGENTS.md` as project documentation.
- Prepared the current Q2 development tree and standalone deliverable for the
  initial `main` branch commit.
- **Superseded:** The initial commit included assignment inputs and generated
  indexes. Automated push review rejected publishing those files because the
  user requested a code push. The local files remain unchanged, while the Git
  commit is being narrowed to source code and documentation only.

### 2026-09-12 — GitHub publication completed

- **Completed:** Initialized the project repository on branch `main`.
- **Completed:** Configured `origin` as
  `https://github.com/whitetiger1399/base-rag.git`.
- **Completed:** Pushed the code-and-documentation commit `957f9f4` to
  `origin/main` and configured the local branch to track it.
- **Confirmed:** Assignment files, source datasets, generated indexes, and the
  virtual environment remain local and are excluded from Git.

### 2026-09-12 — Q2 coding session

- Re-read the assignment and confirmed the Q2 deliverables.
- Inspected all six source workbooks plus Train/Test/SampleSubmission schemas.
- Built and refined the Q2 ingestion, indexes, retrieval, generation, CLI, and UI.
- Corrected Python 3.9 compatibility pins without changing the original lock file.
- Built 787-chunk Chroma and BM25 indexes and verified offline semantic retrieval.
- Verified one grounded cited answer and one correct out-of-domain abstention.
- Verified Streamlit startup and HTTP response, then stopped the test server.
- Packaged the current runnable state under `shared_output/Q2_RAG_Demo/`.

### 2026-09-10 — Session history

- Read the assignment at the user's request without producing a summary then.
- Read the dependency lock file and recorded the environment name.
- Recorded the user's report that Ollama `qwen3:8b` is running.
- Discussed the project layout and revised sharing organization to one folder per task.
- Created the four assignment folders in `shared_output/`.
- The initial root-level agent-file request was interrupted before file creation.
- Followed the revised request by creating `rag-setup/docs/AGENTS.md` with
  section-level append instructions, requirements, plans, and progress.
