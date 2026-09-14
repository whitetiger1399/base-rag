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

### 2026-09-14 — Review v2 requested; documentation only

- **User request:** Re-read the assignment and reassess the implemented v1 action
  plan, then create a separate v2 review of remaining gaps and code structure.
- **Confirmed boundary:** Do not implement changes. Exclude Q2 screenshots/video
  from this review; preserve the previous review and append project history.
- **Evidence / files:** `rag-setup/docs/AGENT_REVIEW_ACTION_PLAN_V2.md`.

### 2026-09-12 — Publish complete project contents

- **User request:** Push everything in the project to the configured Git repository.
- **Superseded:** The earlier code-only GitHub scope is replaced by this request.
- **Confirmed scope:** Track the assignment source, dataset, generated indexes,
  project documentation, demo outputs, and all Q1–Q4 shared deliverables.
- **Environment exception:** Keep the 1.7 GB `rag-setup` virtual-environment
  binaries out of Git because they are machine-specific and reproducible from
  the requirement files; retain `rag-setup/docs/AGENTS.md`.

### 2026-09-12 — Q4 solution request

- **User request:** Complete Q4 according to `Assigment_questions.docx`.
- **Confirmed scope:** Produce the graph-based multi-agent design, required
  Python snippets, and an editable DOCX companion in the Q4 shared-output folder.
- **Confirmed boundary:** These assignment deliverables remain local under
  `shared_output/` and are excluded from the code-only GitHub repository.

### 2026-09-12 — Q3 solution request

- **User request:** Complete Q3 according to `Assigment_questions.docx`.
- **Confirmed scope:** Produce the guardrail, evaluation, and multi-agent design,
  the required Python snippets, and an editable DOCX companion in the Q3
  shared-output folder.
- **Confirmed boundary:** These assignment deliverables remain local under
  `shared_output/` and are not part of the code-only GitHub repository.

### 2026-09-12 — Code-only GitHub scope

- **User request:** Keep only the complete runnable code setup in
  `https://github.com/whitetiger1399/base-rag.git`.
- **Confirmed scope:** Retain root entry points, `src/`, `tests/`, README,
  pytest configuration, and dependency files in Git.
- **Confirmed local-only content:** `shared_output/`, assignment documents,
  datasets, generated indexes, `docs/`, `demo_outputs.md`, `rag-setup/`, and
  other assignment records remain available locally but are excluded from Git.

### 2026-09-12 — Q1 solution request

- **User request:** Start solving Q1 according to `Assigment_questions.docx`.
- **Confirmed scope:** Produce the required 1–2 page retrieval design and
  `snippets_q1.py`, with an editable DOCX companion in the Q1 shared-output folder.

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

### 2026-09-14 — v2 review corrects earlier completion assessment

- **Completed:** Created `rag-setup/docs/AGENT_REVIEW_ACTION_PLAN_V2.md` after
  reading the assignment, current code, PDFs/DOCX text and evaluation artifacts.
- **Confirmed:** Root and packaged tests each report 12 passing tests. Focused
  mocked probes nevertheless exposed chunking, timeout, context-budget,
  Q3 judge and Q4 empty-refinement defects. See v2 for reproducible evidence.
- **Superseded:** The 2026-09-13 blanket completion assessment is not a current
  compliance guarantee. Prior fixes remain recognized, but residual defects and
  stale written deliverables require further work. Demo comparison abstentions
  must not be counted as corpus-unanswerable successes without qualification.
- **Confirmed boundary:** Only review documentation changed; no code, indexes,
  assignment deliverables or v1 content was modified. No live model run or push.
- **Next action:** Await authorization to implement the v2 backlog.

### 2026-09-14 — v2 implementation authorized and applied

- **Completed:** Implemented the actionable v2 runtime fixes and synchronized
  the Q2 package: timeout/config validation, chunk overlap/metadata bounds,
  context accounting, UI/Q1 parameter propagation, Q3 judge/no-progress logic,
  and Q4 refinement/top-k validation.
- **Completed:** Refreshed Q2 design statistics and demo labels and added focused
  regression coverage. Root and packaged tests remain the required validation.
- **Pending:** PDF/DOCX regeneration, evaluation split/annotation audit,
  failure-safe index activation, clean-install/live validation, and Q2 media.
- **Evidence:** See `AGENT_REVIEW_ACTION_PLAN_V2.md` implementation log.

### 2026-09-13 — Action-plan implementation completed except deferred media

| Work item | Status | Evidence / limitation |
| --- | --- | --- |
| Configuration and parameterization | Completed | Validated `Settings`, `MALAWI_RAG_*` overrides, generation budgets, retrieval/RRF/BM25 controls, filter allow-list, and manifest path. |
| Citation/context safety | Completed | Context selection preserves source blocks and derives the citation allow-list from included evidence; malformed and unknown bracketed references are rejected. |
| Q2 demo evidence | Completed except media | Ten observed outputs recorded; three multi-citation answers and three abstentions included. Screenshots/video intentionally deferred by the user. |
| Q3 golden set and metrics | Completed | Added versioned 18-item `golden_set.json`, metric helper, evaluation addendum, and tests for Recall@k, Hit@k, full-evidence recall, and MRR. |
| Q3/Q4 snippet alignment | Completed | Approved-evidence enforcement, unsafe/malformed verdict handling, no-progress routing, idempotent safety filtering, aliases, and retry validation added. |
| Code structure | Completed | Added reusable guardrail/evaluation modules and injected retriever/answer-generator dependencies while retaining thin assignment entry points. |
| Validation | Completed | Twelve tests pass; targeted Q3/Q4 smoke tests pass; local Ollama produced the added demo outputs. |

### 2026-09-13 — Index artifacts synchronized with chunking configuration

- **Completed:** Re-ran ingestion with the explicit one-paragraph overlap and
  produced 1,036 chunks from the six workbooks.
- **Completed:** Rebuilt Chroma and BM25 artifacts offline with the cached local
  embedding model and wrote the matching `storage/manifest.json`.
- **Completed:** Copied the synchronized chunks, indexes, manifest, and source
  modules into `shared_output/Q2_RAG_Demo/`.
- **Completed:** Recaptured the ten Q2 demo outputs against the current
  1,036-chunk manifest and updated both demo records. The long One Health answer
  is explicitly marked as output-token limited; the deterministic fallback
  validator was also exercised on the Chikungunya/diabetes comparison.

### 2026-09-12 — Q4 graph-based multi-agent RAG completed

| Work item | Status | Evidence / limitation |
| --- | --- | --- |
| Graph design | Completed | Defines typed shared state, Retriever, Safety, Verifier, Answerer, and Abstain nodes with explicit outputs and invariants. |
| Conditional routing | Completed | Routes sufficient evidence to Answerer, unsafe evidence to filtering/re-verification, incomplete evidence to refined retrieval, and terminal failures to abstention. |
| Bounded retries | Completed | Initial retrieval plus at most two Verifier-to-Retriever returns; Answerer and Abstain terminate the graph. |
| Required snippets | Completed | `snippets_q4.py` provides `GraphState`, node functions, conditional routing, injection filtering, citation validation, and a dependency-free executor. |
| Code validation | Completed | Python 3.9 compilation passed. Smoke tests covered a successful cited answer and poisoned evidence with exactly two retries followed by abstention. |
| PDF deliverable | Completed | Three-page PDF generated and every page visually inspected; no clipping, overlap, broken glyphs, broken tables, or missing visible content found. |
| DOCX companion | Completed | Letter geometry, one-inch margins, two page breaks, required terms, and four fixed-width tables passed structural audit. |
| DOCX render limitation | Confirmed | LibreOffice is not installed, so DOCX-to-image visual QA was unavailable. The matching PDF was rendered separately and fully inspected. |

Q4 files:

- `shared_output/Q4_Graph_Multi_Agent/graph-based-multi-agent.pdf`
- `shared_output/Q4_Graph_Multi_Agent/graph-based-multi-agent.docx`
- `shared_output/Q4_Graph_Multi_Agent/snippets_q4.py`

### 2026-09-12 — Q3 guardrails, evaluation, and agent plan completed

| Work item | Status | Evidence / limitation |
| --- | --- | --- |
| Guardrail design | Completed | Defines trust boundaries, retrieved-text injection screening and quarantine, evidence gating, exact citation validation, abstention, and public-health tone controls. |
| Evaluation plan | Completed | Defines an 18-question golden set, Recall@4, MRR, faithfulness, citation quality, abstention, injection safety, initial release gates, and human review. |
| Multi-agent plan | Completed | Specifies Retriever, optional Safety, Verifier, and Answerer contracts; structured routing; two bounded retrieval retries; and terminal abstention. |
| MLflow plan | Completed | Defines batch/question runs, parameters, metrics, sanitized traces, artifacts, corpus/model/prompt versioning, and privacy-aware logging. |
| Required snippets | Completed | `snippets_q3.py` implements the required injection detector, local-Ollama faithfulness scorer, and minimal dependency-injected orchestration; it compiles under Python 3.9 and passed detector smoke checks. |
| PDF deliverable | Completed | Three-page PDF generated and every page visually inspected; no clipping, overlap, broken tables, or missing visible text found. |
| DOCX companion | Completed | Letter geometry, one-inch margins, two page breaks, required content, and three fixed-width tables passed structural audit. |
| DOCX render limitation | Confirmed | LibreOffice is not installed, so DOCX-to-image visual QA was unavailable. The matching PDF was rendered separately and fully inspected. |

Q3 files:

- `shared_output/Q3_Guardrails_Eval_Agents/Q3_Guardrails_Eval_Agents.pdf`
- `shared_output/Q3_Guardrails_Eval_Agents/Q3_Guardrails_Eval_Agents.docx`
- `shared_output/Q3_Guardrails_Eval_Agents/snippets_q3.py`

### 2026-09-12 — Q1 retrieval design completed

| Work item | Status | Evidence / limitation |
| --- | --- | --- |
| Q1 design content | Completed | Two-page design grounded in the actual six-workbook dataset and working Q2 implementation. |
| Required retrieval topics | Completed | Covers structure-aware chunking, metadata, vector vs. hybrid retrieval, top_k selection, and local reranking/fusion. |
| Required snippets | Completed | `snippets_q1.py` contains all three required function signatures and compiles under Python 3.9. |
| PDF deliverable | Completed | Two-page PDF generated and every page visually inspected; no clipping, overlap, broken table, or missing text found. |
| DOCX companion | Completed | Letter geometry, margins, page break, metadata table widths, and table cell widths passed structural audit. |
| DOCX render limitation | Confirmed | LibreOffice is not installed; DOCX-to-PNG visual QA was unavailable. The PDF was generated separately and passed full visual QA. |

Q1 files:

- `shared_output/Q1_Retrieval_Design/Q1_Retrieval_Design.pdf`
- `shared_output/Q1_Retrieval_Design/Q1_Retrieval_Design.docx`
- `shared_output/Q1_Retrieval_Design/snippets_q1.py`

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

### 2026-09-14 — Documentation-only reassessment

- **Completed:** Added `AGENT_REVIEW_ACTION_PLAN_V2.md` with remaining findings,
  acceptance criteria, implementation order and review limitations. Preserved v1
  and appended this record. Q2 screenshots/video were excluded as requested.

### 2026-09-13 — Action-plan implementation session

- Implemented the authorized review backlog while leaving Q2 screenshots/video
  deferred at the user's request.
- Added validated configuration, bounded generation context, citation checks,
  retrieval/index parameters, reusable guardrail/evaluation modules, a concrete
  golden set, and graph/snippet alignment.
- Captured and documented the remaining real local Q2 runs; updated the root and
  standalone package from the same source modules.
- Validation completed with nine automated tests and targeted Q3/Q4 smoke tests.

### 2026-09-12 — Q4 graph workflow session

- Re-read the Q4 requirements and mapped the working Q2 retriever and Q3
  guardrails into explicit graph state, node, edge, and termination contracts.
- Implemented a dependency-free graph executor with an optional Safety stage,
  refined-query retrieval loop, exact citation allow-list, bounded retries, and
  deterministic abstention.
- Generated a three-page design PDF and editable DOCX companion.
- Compiled and smoke-tested both success and adversarial graph paths, audited
  DOCX structure, and visually inspected every rendered PDF page.

### 2026-09-12 — Q3 guardrails, evaluation, and multi-agent session

- Re-read the Q3 requirements and aligned the design with the working Q2 hybrid
  retriever, exact citation IDs, abstention behavior, and local `qwen3:8b` model.
- Created a three-page business-brief design covering layered guardrails, an
  18-question golden set, retrieval and generation metrics, four agent contracts,
  bounded routing, and MLflow observability.
- Created the required shareable Python functions and orchestration example.
- Compiled the snippet, smoke-tested injection detection, structurally audited
  the DOCX, and visually inspected all three rendered PDF pages.

### 2026-09-12 — Q1 retrieval design session

- Re-read the Q1 requirements and reviewed the implemented chunking, indexing,
  BM25, hybrid retrieval, metadata, and threshold configuration.
- Created a two-page `standard_business_brief` retrieval design using a
  restrained memo-style opening and an explicit metadata field table.
- Created the required real-code wrapper snippets for chunking, index building,
  and filtered top-k retrieval.
- Generated and visually inspected both PDF pages at high resolution.
- Audited the DOCX's page geometry, margins, page break, and fixed table geometry.

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

### 2026-09-14 — Documentation correction pass

- **Completed:** Refreshed current Q1/Q2/Q3 documentation with the 1,036-chunk
  corpus and corrected Recall@4 wording; Q1/Q3 Word and PDF companions were
  updated in place while preserving their structure.
- **Limitation:** DOCX rendering could not run because `soffice` is absent.
  Historical 787-chunk references remain as dated evidence of the earlier corpus,
  not as current project statistics.

### 2026-09-14 — Chunking strategy documented

- **Completed:** Added the row-to-chunk explanation to the root and packaged Q2
  design docs, including the TG Booklet 3 2,064-entry to 213-chunk example and
  paragraph provenance behavior.

### 2026-09-10 — Session history

- Read the assignment at the user's request without producing a summary then.
- Read the dependency lock file and recorded the environment name.
- Recorded the user's report that Ollama `qwen3:8b` is running.
- Discussed the project layout and revised sharing organization to one folder per task.
- Created the four assignment folders in `shared_output/`.
- The initial root-level agent-file request was interrupted before file creation.
- Followed the revised request by creating `rag-setup/docs/AGENTS.md` with
  section-level append instructions, requirements, plans, and progress.
