# Malawi RAG — Agent Review and Action Plan

Review date: 2026-09-13 (Asia/Singapore)
Status: Implementation completed for all requested points except Q2 screenshots/video, which the user explicitly deferred.
Assignment authority: `Assigment_questions.docx` at the project root.
Paths in this document are relative to the project root.

## 1. Instructions to the next agent

The user subsequently authorized implementation of this plan, explicitly excluding Q2 screenshots/video.

- Keep remaining checklist items visible; do not claim screenshots/video are complete.
- Preserve the existing `rag-setup/docs/AGENTS.md` history. This file supplements it; historical completion claims are not proof of current compliance.
- After implementation is separately requested, append dated progress under the relevant sections. Record evidence and remaining limitations; do not replace this review wholesale.
- Preserve the user's selected six-chunk default while adding validation and environment overrides.
- Separate assignment requirements from optional engineering improvements. Q3 and Q4 request designs and short snippets; a deployed multi-agent service, LangGraph dependency, and operational MLflow server are not mandatory.

## 2. Overall assessment

The project is a useful implementation foundation but is **not ready to declare fully compliant**. Q1 substantially covers its requested topics. Q2 has the core implementation but incomplete demonstration evidence and a current configuration regression. Q3 has the required design topics and snippets, but no concrete golden question set and several snippet contract gaps. Q4 has state, nodes, routing, and bounded retries, but its code does not consistently match its write-up.

Existing classes (`Settings`, `Chunk`, `RetrievedChunk`, `BM25Index`, `HybridRetriever`, `MalawiRAG`) are a good starting point. Improve their boundaries and validation; converting every helper into a class would add complexity without improving correctness.

## 3. Requirement-by-requirement review

| Requirement | Status and evidence | Remaining work |
| --- | --- | --- |
| Q1: 1–2-page retrieval design | Present: `shared_output/Q1_Retrieval_Design/Q1_Retrieval_Design.pdf`, two pages | Reconcile implementation claims listed below. |
| Q1: headings, lists, small/long sections, metadata | Covered in PDF; ingestion and metadata exist | Validate list continuity and overlap claims against actual chunking. |
| Q1: vector vs hybrid, top_k, local reranking | Covered; local RRF satisfies the permitted fusion option | Describe vector-only limitations as a design rationale, not a measured comparison. |
| Q1: three snippets | Present in `snippets_q1.py`, backed by root modules | Explain dependency on the root package and invocation context. |
| Q2: ingestion, chunking, embedding index | Implemented; saved chunk and index artifacts present | Verify fresh rebuild consistency and safe index replacement. |
| Q2: local LLM and query interface | Ollama generation, CLI, and Streamlit code present | Fix current generation settings; rerun locally with recorded evidence. |
| Q2: citations and abstention | Implemented baseline, but validation is limited | Repair citation checks and test insufficient-evidence cases. |
| Q2: trace with chunks and score/rank | Streamlit displays source text and scores | CLI trace prints metadata/scores but not chunk text; align it if advertised as a full evidence trace. Streamlit already provides the required interface path. |
| Q2: ten questions and outputs | Completed | Both demo files contain ten current-index observed runs with questions, answers, citations, and traces. |
| Q2: at least two correct abstentions | Completed | Four abstention outcomes recorded, including out-of-domain, unsupported comparison, and personal-advice cases. |
| Q2: at least two multi-chunk answers | Completed | Indicator-based surveillance and One Health outputs cite multiple distinct chunks. |
| Q2: screenshots or short video | **Missing:** no media files found in shared outputs | Capture the running interface with answers and trace visible. |
| Q2: required runnable files | All named entry points and README present in package | Fresh-install/run validation remains necessary. |
| Q3: injection, output constraints, public-health tone | Covered in three-page PDF and snippets | Correct code/write-up discrepancies; distinguish planned controls from implemented Q2 controls. |
| Q3: golden set of 15–20 questions | **Incomplete artifact:** PDF proposes 18 categories/items but supplies no actual question list | Create 15–20 concrete questions and annotations. This conservatively satisfies “create golden set” within the evaluation-plan task. |
| Q3: Recall@k, MRR, faithfulness | Discussed; scoring snippet present | Correct recall definition and specify scoring cohorts, evidence sets, and failure policy. |
| Q3: agent contracts and MLflow use | Design present | Operational integration is optional, not an assignment blocker. |
| Q4: state, nodes, outputs | Present in three-page PDF and `snippets_q4.py` | Align field names, node contracts, and documented failure behavior. |
| Q4: insufficient → refined retrieval | Exists for valid verifier refinements | All-filtered path repeats the same query; improve or explicitly stop on no progress. |
| Q4: injection → filter → re-verify | Safety filters before verification | Preserve verification of remaining clean evidence; cover mixed/all-filtered inputs. |
| Q4: stopping and abstention | Default two retries bounds normal execution | Validate retry inputs, reject malformed verdicts, and test all terminal paths. |

## 4. Priority findings and acceptance criteria

### P0-01 — Current root settings break generation — Resolved

Evidence: latest `src/config.py` sets `answer_top_k=6` and omits `max_context_chars` and `max_answer_tokens`. `src/generation.py::generate_answer` still accesses both. The packaged Q2 configuration retains both fields and defaults to four chunks. The root file changed during the review; this finding applies to the latest observed state, not the earlier committed configuration.

Resolution: `Settings` now validates generation budgets and root/package configurations are synchronized. The user's six-chunk default is retained.

Required future action: agree on the intended defaults, restore a complete validated configuration contract, and synchronize the generated submission package after validation. Do not revert the user's six-chunk preference silently.

Acceptance: a query reaching generation can construct its request using the current settings; a mock HTTP integration check detects missing settings; a live local demonstration succeeds. Root and package differences are deliberate and documented.

### P0-02 — Complete Q2 demonstration evidence — Resolved except deferred media

Evidence: `demo_outputs.md` and `shared_output/Q2_RAG_Demo/demo_outputs.md` explicitly say work in progress and contain only CBS and engine-oil questions. The CBS answer cites one chunk; the other abstains. No screenshots/video were found.

Resolution: both demo files now contain ten current-index observed outputs, four abstentions, and two multi-citation answers. Screenshots/video remain deferred by user instruction.

Required future action: capture ten real runs with question, exact output, citation IDs, relevant trace, model/configuration, and outcome. Include two correct abstentions and two genuinely supported multi-chunk answers. Capture screenshots or a short video of the running app.

Acceptance: ten reproducible records and media exist in the Q2 deliverable; a reviewer can locate each cited passage. Do not fabricate outputs or label hypothetical answers as observed.

### P1-01 — Citation allow-list and actual context must agree

Evidence: `src/generation.py::citations_are_valid` only recognizes IDs matching its citation regex. A probe containing a valid ID and `[invented]` returns True. It requires at least one citation, not support/citation coverage for every factual claim. `build_context` slices blocks at a character limit, while the allow-list includes every retrieved chunk, including evidence potentially omitted by truncation.

Required future action: use one parsed citation contract, explicitly reject malformed/unknown source references, and construct the allow-list from evidence actually sent. Budget prompt, question, source metadata, evidence, and output together; preserve passage boundaries. Keep citation validity separate from semantic support.

Acceptance: mixed valid/unknown references fail; omitted chunks cannot be cited; truncation is explicit; unsupported extra claims are caught by the selected validation policy. The UI/trace distinguishes retrieved evidence from evidence sent to generation.

### P1-02 — Q3 orchestration does not enforce its approved-evidence contract

Evidence: `snippets_q3.py::run_agents` passes all safe chunks to Answerer and ignores `approved_ids`. A mocked scorer returning 1.0 allowed `Fact [b] [unknown]` even when the verifier approved only `a`. The snippet does not implement the documented query safety/tone check. Quarantine IDs reset per attempt.

Required future action: restrict generation to approved IDs, validate all citation IDs before semantic scoring, explicitly handle unsafe verdicts and abstention, and retain attempt-level safety history. Either implement additional checks in the example or clearly label them as design extensions.

Acceptance: unapproved evidence never reaches Answerer; unknown IDs fail before scoring; unsafe requests have a terminal policy; the example and PDF describe the same behavior.

### P1-03 — Faithfulness scorer needs a defensible result contract

Evidence: `faithfulness_check` accepts a model-generated scalar and clamps it; there is no claim list, schema/type/finite-number validation, explicit service-failure outcome, or evidence-length budget. The prompt requests a score of 1.0 when there are no factual claims. Caller and verifier evidence remain untrusted.

Required future action: define atomic claims, per-claim cited evidence and support verdicts, then compute the score from validated results. Define empty-answer, exact-abstention, malformed JSON, timeout, non-finite score, and over-budget outcomes. Keep the required public function signature or provide a small compatible wrapper. Inject the local client/settings for tests.

Acceptance: invalid results cannot pass; abstention is evaluated separately; deterministic tests cover malformed responses and unsupported claims. Human review calibrates the local judge; model judgment alone is not proof of factual correctness.

### P1-04 — Q3 evaluation plan needs actual items and correct metrics

Required future action: create a versioned 15–20-item JSON/CSV golden set with IDs, questions, answerability, expected facts, document/paragraph references, relevant chunk IDs tied to a corpus version, category, and expected safety behavior. Separate malicious-passage fixtures from clean question text. Do not claim independent review until it happens.

The PDF's “a gold chunk appears” definition is Hit@k, not set-based Recall@k for multiple relevant chunks. Specify:

- Recall@k = |retrieved top-k intersect gold relevant set| / |gold relevant set|.
- Hit@k = whether at least one relevant chunk appears.
- Full-evidence recall = whether all required evidence appears.
- MRR = mean reciprocal first relevant rank, zero when absent.
- Compute retrieval metrics on answerable cases with nonempty gold sets; evaluate abstention separately.

Acceptance: concrete items exist; denominators and retrieval cutoffs are explicit; tuning and held-out cases are separated. Six held-out cases cannot support precise 95% claims, especially for tiny safety subsets. Report counts and limitations, and describe thresholds as proposed targets unless measured. An evaluation runner and recorded baseline are recommended enhancements, not a required production service.

### P1-05 — Q4 snippet and write-up disagree on routing and failures

Evidence: `route_after_verification` routes an unknown verdict with a refinement back to retrieval (confirmed with `garbage`), whereas the PDF says malformed verdicts abstain. `verification_node` repeats `active_query` when all evidence is filtered and skips the verifier. Provider exceptions propagate despite the write-up describing explicit failure outcomes. `safety_node` appends to lists without clearing them itself. Trace records raw query text despite redaction-oriented prose. The state does not contain all documented fields such as `max_retries` or confidence.

Required future action: validate verifier schemas/enums and approved IDs; make routing explicit for each verdict; provide a real refinement or a no-progress stop; distinguish configuration from state; normalize node failures and abstention reasons. Make safety re-entry idempotent and reconcile trace privacy claims with actual data. Expose top_k at graph entry and validate retry bounds. Preserve the original question.

Acceptance: tests cover sufficient, refined success, mixed injection, all-filtered evidence, repeated query, malformed verifier result, invalid IDs, unsafe request, timeout, and exhausted retries. Default execution uses at most three retrieval attempts. Document that local Ollama/Q2 adapters are required: Q2 returns `RetrievedChunk` objects while the snippet expects mappings. Match requested node names (`retrieve_node`, `verify_node`) or provide explicit aliases/mapping. LangGraph adoption is optional.

### P1-06 — Chunking correctness and evidence preservation

Evidence: `chunk_booklet` joins rows by size/punctuation and can split lists without list-aware grouping. `flush` retains overlap only when accumulated size already reaches the maximum, so ordinary target-sized flushes lack the overlap described in Q1. Header text adds to the body size limit. `split_long_text` subtracts a fixed 200-character reserve without validating parameters. Consecutive headings may replace parent heading context.

Required future action: specify body versus complete-chunk limits, heading hierarchy, list boundaries, minimum section handling, and overlap semantics. Validate `0 < target <= maximum` plus any reserve. Check source coverage, duplication, and citation provenance on synthetic edge cases and the actual workbook corpus.

Acceptance: no accidental content loss; bounded complete chunks; list qualifiers stay attached where possible; overlap is predictable. Update Q1 claims to reflect the selected implementation rather than asserting preservation that has not been tested.

### P1-07 — Index rebuild and retrieval configuration safety

Evidence: `build_index` deletes the existing collection before encoding succeeds and catches all deletion exceptions. Vector and BM25 artifacts can become inconsistent after partial failure. No corpus/model/configuration manifest is checked at query time. Hybrid retrieval accepts unvalidated k and filter keys; vector/BM25 treatment of empty filters differs. Retrieval candidate count is not capped to available records.

Required future action: validate inputs and model/index compatibility; build a versioned replacement before switching; catch specific expected errors; persist a shared corpus/index manifest. Normalize filters once and validate k. Parameterize candidate multipliers, RRF constant, BM25 parameters, and batch size.

Acceptance: a failed rebuild leaves the previous working index available; both retrieval stores share chunk IDs/version; invalid k/filters fail clearly; small or empty collections have defined behavior.

## 5. Proposed structure and class responsibilities

This is a future design, not an instruction to create these files now. Keep root entry points required by Q2 as thin wrappers.

```text
malawi-rag/
  app.py, ingest.py, index.py, rag.py
  src/
    config.py        # validated settings and loading
    models.py        # typed requests, evidence, verdicts, responses
    chunking.py      # loader/chunker and pure normalization helpers
    indexing.py      # index builder and manifest
    bm25.py          # existing BM25Index
    retrieval.py     # HybridRetriever
    generation.py    # Ollama client and answer service
    guardrails.py    # citation and evidence policy, when implemented
    evaluation.py    # optional reproducible evaluation runner
    graph.py         # optional application integration of Q4 design
  tests/
  docs/
  scripts/          # reproducible submission packaging, if needed
  shared_output/    # retain existing per-question deliverables
  rag-setup/docs/   # preserve requested agent records
```

| Component | Suggested responsibility and dependency boundary |
| --- | --- |
| Settings | Validated immutable configuration; no service initialization during import. |
| Chunk / RetrievedChunk | Preserve existing typed evidence models and metadata. |
| OllamaClient | Own request serialization, local URL/model configuration, timeout, and response validation; injectable HTTP transport. |
| AnswerGenerator | Build bounded context and source allow-list, generate, and validate the answer contract. |
| HybridRetriever | Own retrieval/fusion; accept injected embedding/index dependencies for meaningful tests. |
| IndexBuilder | Own versioned build lifecycle and artifact manifest. |
| MalawiRAG | Coordinate retrieval, evidence gating, and generation through injected interfaces. Avoid constructing every concrete dependency inside its constructor. |
| VerificationResult / RAGResponse | Explicit verdict enum, approved IDs, missing facts, abstention reason, and source provenance. |
| GraphRunner | Only if runtime integration is requested: own bounded transitions and state; use typed provider adapters. |

Prefer composition and small Protocol interfaces where two implementations or test substitutes are useful. Keep pure text/metric functions as functions. Avoid a framework-heavy hierarchy for this small assignment.

## 6. Parameterization plan

Introduce one documented loading path: built-in defaults, optional config file, environment overrides, then explicit CLI overrides. Select and document this precedence before implementation. Pass resolved Settings into services and key Streamlit caching on relevant configuration.

| Group | Parameters to centralize and validate |
| --- | --- |
| Paths | Dataset, storage root, chunk manifest, collection, BM25, output artifacts; derive children consistently. |
| Chunking | Target, maximum, metadata reserve, overlap, minimum section policy. |
| Retrieval | Answer top_k, candidate count/multiplier, RRF constant, BM25 k1/b, filter allow-list, evidence thresholds. |
| Generation | Local model and URL, request timeout, temperature, context token budget, output tokens, evidence budget. |
| Indexing | Embedding model/revision, batch size, download/offline policy, manifest version. |
| Graph/evaluation | Retry count, node timeouts, faithfulness threshold, optional tracking URI, redaction mode, evaluation split. |

Acceptance: users can change model, top_k, paths, and timeout without editing source; invalid values fail before retrieval; effective settings are recorded with demos. All entry points and shared package use the same intended defaults. Validate configuration fields consumed by generation, not only dataclass construction.

## 7. Documentation and packaging corrections

- Root README says datasets/indexes are excluded from Git, but they were published in `b0997e9`. Update this statement in a future documentation pass.
- Root and packaged config now differ materially. Establish a single source of truth and reproducible packaging/checksum comparison; avoid hand-maintaining duplicate implementations.
- Q1 describes parallel vector/BM25 search and retaining larger candidates in trace; current retrieval executes sequentially and returns only final top-k. Label these as proposed behavior or align the implementation if justified.
- Do not claim hybrid superiority or tuned thresholds without a measured comparison.
- Q3/Q4 are design/snippet deliverables, not integrated agents in `src/rag.py`; explain this clearly.
- PDFs and DOCX companions were separately authored in prior work. Review their content parity and render DOCX when tooling is available before claiming visual equivalence. This review extracted PDF text/page counts; it did not visually re-audit documents.
- Keep public repository scope consistent with the latest user request. Do not remove published datasets or indexes as part of an unapproved refactor.
- Validate installation on the documented Python/platform combination in a clean environment. Existing environment tests do not prove fresh-install portability.

## 8. Validation performed in this review

- Extracted the complete assignment text directly from DOCX XML.
- Inspected implementation modules, root entry points, tests, dependency declarations, demo outputs, agent history, and Q1/Q3/Q4 snippets.
- Extracted design PDF text: Q1 has 2 pages; Q3 and Q4 have 3 pages each.
- The initial review ran the pre-change suite with bytecode/cache writing disabled: **6 passed**. The implementation pass expanded it to **11 passed**, including generation budgets, citation/context boundaries, guardrails, and retrieval metrics.
- Ran in-memory probes confirming mixed malformed citation acceptance, Q3 unapproved citation acceptance with a mocked faithfulness result, and Q4 malformed-verdict retry routing.
- Compared root/package source files and confirmed current config drift. Verified the two required generation fields are absent from root Settings.
- Did not call live Ollama, reinstall dependencies, rebuild indexes, modify implementation, regenerate deliverables, or push changes. No live runtime performance or semantic faithfulness claim is made by this review.

## 9. Suggested execution order after separate authorization

1. Fix the settings contract and add a meaningful generation-path regression test.
2. Correct citation/context handling and align Q3/Q4 snippets with their documents.
3. Supply the concrete golden set and clarify metrics/annotation rules.
4. Complete ten real Q2 outputs and required media using validated settings.
5. Introduce dependency injection and consolidated configuration incrementally; validate chunk/index invariants.
6. Reconcile documentation and regenerate the shared package from the canonical code.
7. Run fresh-install and end-to-end checks, record actual results, then review assignment compliance again.

## 10. Completion checklist for a future implementation pass

- [x] Root generation works with current Settings and intended top_k.
- [x] Q2 has ten observed outputs, four abstention cases, and two supported multi-chunk answers.
- [ ] Required screenshots or video exist (explicitly deferred by the user).
- [x] Q3 includes 18 actual annotated questions and unambiguous metric definitions.
- [x] Q3 approved-evidence/citation contract is enforced in the shareable snippet.
- [x] Q4 refinement, filtering/re-verification, schema failures, and retry bounds match the implementation.
- [x] Context allow-list reflects evidence actually provided to the model.
- [x] Configuration, root code, package, and README agree.
- [x] Tests cover observed regressions and meaningful failure paths.
- [x] Assignment evidence is distinguished from optional engineering extensions.
- [x] Completion claims include automated, targeted, and local-run evidence.

## 11. Review activity log

### 2026-09-13 — Documentation-only review

Created this action plan before implementation authorization. Findings described
work still needed and preserved the user's configuration edit at that time.

### 2026-09-13 — Authorized implementation pass

- **Completed:** Added validated, parameterized `Settings` with environment
  overrides, generation budgets, retrieval/RRF/BM25 parameters, filter allow-list,
  and an index manifest path. Preserved the user's six-chunk default.
- **Completed:** Added bounded context selection so the citation allow-list only
  includes evidence actually sent to the model; malformed or unknown bracketed
  references now fail validation. Added generation-path and configuration tests.
- **Completed:** Added retrieval input validation, configurable RRF/BM25 values,
  explicit chunking parameter validation and paragraph overlap, injectable RAG
  retriever/answer-generator dependencies, and CLI trace source text.
- **Completed:** Added reusable `src/guardrails.py` and `src/evaluation.py`, a
  concrete 18-item `golden_set.json`, metric definitions/addendum, and tests for
  Recall@k, Hit@k, full-evidence recall, and MRR.
- **Completed:** Aligned Q3 orchestration with approved evidence, unsafe-query
  handling, citation validation, malformed verifier handling, and faithfulness
  failure behavior. Aligned Q4 graph safety re-entry, malformed verdict routing,
  no-progress stopping, aliases, and retry validation.
- **Completed:** Captured ten observed Q2 demo questions and outputs, including
  two multi-citation answers and four abstention cases. Updated root and
  packaged demo records and synchronized root/package source files.
- **Deferred by user:** Q2 screenshots or video remain outstanding.
- **Validation:** The suite now reports 12 passing tests; targeted Q3/Q4 smoke
  tests pass; local Ollama runs produced the added observed Q2 outputs.
