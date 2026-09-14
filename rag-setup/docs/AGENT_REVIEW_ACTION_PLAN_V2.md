# Malawi RAG — Agent Review and Action Plan v2

Review date: 2026-09-14 (Asia/Singapore)  
Reviewed baseline: `89b7abb` (`Implement RAG review action plan`)  
Status: **Implementation completed for the actionable runtime/documentation items; Q2 screenshots/video remain deferred.**  
Assignment authority: `Assigment_questions.docx`  
Previous review: `rag-setup/docs/AGENT_REVIEW_ACTION_PLAN.md`

## 1. User request and agent boundaries

Reassess the current project against the assignment after the previous implementation pass. Identify what is still missing or needs improvement, including parameterization, class responsibilities, and code structure. Produce this separate v2 document without changing code or assignment deliverables.

- Exclude Q2 screenshots/video from this review and its completion gates, as explicitly requested. Their exclusion is not a claim that the original assignment's media requirement has been fulfilled.
- Preserve v1 as historical evidence. This review supersedes its blanket completion claims for the current assessment.
- Do not implement this backlog, regenerate indexes/documents, install dependencies, or push changes until requested.
- Append future dated implementation evidence under the relevant sections and activity log; do not overwrite this document wholesale.
- Preserve the user's six-chunk default and per-question `shared_output/` organization.
- Q1, Q3, and Q4 ask for designs and short snippets. A production graph service, LangGraph adoption, deployed MLflow server, and converting every function into a class are **not mandatory**.

## 2. Problem statement and overall assessment

The project must provide a local Malawi public-health RAG demonstration that retrieves evidence, produces cited answers, abstains when evidence is insufficient, and exposes retrieval traces. Companion assignments explain retrieval design, safety/evaluation/agent contracts, and a bounded graph workflow.

**The project substantially covers the assignment, but the previous “all requested points completed” conclusion is too strong.** The core Q2 implementation and required text artifacts exist. Several earlier defects were fixed. Remaining correctness problems affect chunking, configuration, graph routing, judge validation, and consistency between the current code and written deliverables. Passing the current 12 tests does not establish full compliance.

The highest priorities are to correct confirmed runtime defects and reconcile the submitted documents and demo claims. Wider infrastructure refactoring should follow those corrections, not precede them.

## 3. What is already implemented — do not redo unnecessarily

| Earlier issue | Current evidence | Assessment |
| --- | --- | --- |
| Missing generation configuration fields | `Settings` now contains context and output budgets | Fixed; generation request construction was exercised with a mock transport. |
| Root/package configuration drift | Compared root and packaged `src/*.py`, entry points, README, requirements, and Q2 design document byte-for-byte | No differences in the compared files. |
| Citations to omitted context or unknown bracketed IDs | `_select_context` supplies an included-source allow-list; mixed valid/unknown citations are rejected | Main defect fixed; budgeting and claim-level coverage still need work. |
| CLI trace missing evidence text | `rag.py` prints `item.chunk.text` | Fixed. Streamlit also exposes text and scores. |
| Missing concrete golden set | Q3 JSON has 18 items; every referenced chunk ID exists in the current JSONL | Artifact supplied; annotation quality/splits/attack fixtures remain incomplete. |
| Incorrect metric implementation | `src/evaluation.py` distinguishes set Recall@k, Hit@k, full-evidence recall, and reciprocal rank | Helper corrected; PDF/DOCX definition remains stale. |
| Q3 unapproved sources reaching Answerer | `run_agents` restricts input to approved chunks and rejects unknown answer IDs | Fixed for ordinary well-formed verifier responses. |
| Q4 unknown-verdict routing and safety duplication | Unknown verdict strings abstain; safety rebuilds filtered lists on re-entry; required aliases exist | Fixed in part; empty refinements and malformed field types remain problematic. |
| Dangerous deletion before embedding failure | Indexer computes embeddings before deleting the old collection | Improved, but replacement is not atomic. |
| Demo record incomplete | Both demo files contain ten question/output records and two multi-citation examples | Present; provenance, truncation, and outcome labels need correction. |

## 4. Assignment compliance matrix

| Requirement | Current assessment | Remaining action |
| --- | --- | --- |
| Q1: 1–2-page design and required snippets | PDF is two pages; all three interfaces exist | Correct outdated measured statistics and distinguish proposed behavior from implemented behavior (V2-01). |
| Q1: headings, lists, small/long sections, metadata | Discussed; structured ingestion and metadata exist | Correct chunking invariants and overly strong list-preservation claims (V2-02). |
| Q1: vector vs hybrid, top_k, local reranking | Covered; RRF is an allowed local fusion approach | Retain rationale; do not imply measured superiority without comparison. |
| Q2: ingestion, local embedding index, local LLM, CLI/UI | Implemented; saved indexes and all required entry points present | Remaining reliability/configuration fixes; clean installation and live end-to-end operation were not revalidated today. |
| Q2: citations and insufficient-evidence fallback | Baseline implemented and tested | ID validity is not proof that all claims are grounded; handle truncation and budget limits (V2-04). |
| Q2: trace text and scores/ranks | Present in CLI and UI | Optional improvement: label quarantined, context-selected, and cited evidence separately. |
| Q2: ten outputs, two abstentions, two multi-citation answers | Ten records; out-of-domain and personal-advice abstentions; two examples list multiple IDs | Preserve exact outputs and verify supporting citations; correct answerable-comparison labels (V2-05). |
| Q2: runnable package | Named files, dependencies, and source copy present | Validate documented setup in a clean environment; automate copy parity if maintaining duplicate source. |
| Q3: safety, tone, agent responsibilities and MLflow use | Covered in three-page PDF and snippets | Separate implemented screening from planned semantic/policy controls; repair judge/orchestration contracts (V2-06). |
| Q3: golden set and retrieval/faithfulness evaluation | 18-item set, addendum, metric helper present | Correct PDF/DOCX metrics; validate annotations, freeze split, add retrieved-text attack fixtures (V2-07). |
| Q4: state, nodes, conditions and retry limit | Three-page PDF and dependency-injected state machine present | Repair empty-refinement route, validate schemas, reconcile failure handling (V2-08). |
| Q4: injection filtering and re-verification | Clean remainder is passed to Verifier; all-filtered case stops on no progress | Document that all-filtered evidence currently stops rather than performing the refinement described in the PDF. |

## 5. Remaining findings and acceptance criteria

### V2-01 — P1: Submitted write-ups still describe the old implementation

**Evidence:** Q1 PDF page 1 and its DOCX still report 787 chunks and a maximum of 2,663 characters. Current JSONL contains 1,036 chunks, with maximum length 4,868. Root and packaged `docs/Q2_DESIGN.md` retain the old statistics and four-chunk default. Q1 page 2 describes parallel retrieval and retaining the larger candidate pool for trace; `HybridRetriever.retrieve` executes the two searches sequentially and returns only final top-k. Q3 PDF/DOCX define Recall@4 as whether any gold chunk appears, which is Hit@4. The Markdown addendum corrects this but the required PDF itself remains wrong. Q4's failure/schema prose also disagrees internally and with the snippet (see V2-08).

**Future action:** Update the required PDFs and DOCX companions together after code corrections. Clearly label intended design choices, actual measurements, and optional extensions. Refresh Q2 design text and v1 status via an appended correction rather than erasing history. Keep Q1 within two pages.

**Acceptance:** All stated corpus statistics come from the final artifacts; CLI/UI defaults are explained accurately; Recall@k is set-based in the PDF itself; no unimplemented parallelism, candidate trace, schema validation, or failure policy is presented as current behavior. Render and inspect regenerated documents when implementation is authorized.

### V2-02 — P1: Chunk overlap and limits are still incorrect

**Evidence:** `src/chunking.py::chunk_booklet` retains `pending[-overlap_paragraphs:]`; Python's `[-0:]` retains the whole list rather than disabling overlap. After `flush`, retained overlap plus the incoming row is not checked again against the limit. Final flushing can emit overlap-only duplicate chunks. The fixed `max_chars - 200` reserve can become zero or negative despite accepted public configuration. Consecutive headings replace earlier heading context; list grouping is size/punctuation driven rather than explicitly list-aware.

**Confirmed probes:** Synthetic three-row input with target 300/max 500 produced six chunks with repeated paragraph ranges for both overlap 0 and 1. A ten-character source with target 5/max 10 produced **zero chunks**, silently dropping the source. In the saved corpus, **161 of 1,036 complete chunk texts exceed 2,600 characters**, and the largest is 4,868. A small excess could come from section prefixes; the observed maximum requires more than that explanation.

**Future action:** Define whether limits apply to body or complete text; account for heading overhead consistently. Handle zero overlap explicitly, cap retained context before appending, and prevent final overlap-only output. Reject unsupported size/reserve combinations before processing. Specify list qualifiers and heading hierarchy rather than promising untested preservation.

**Acceptance:** Regression cases cover zero/multiple overlap, large adjacent paragraphs, final flush, tiny limits, consecutive headings, and lists. Every nonempty source row is covered or explicitly classified; no accidental duplicates or overflow beyond the stated contract. Any rebuild must update all dependent indexes, gold references, demo records, and package copies together.

### V2-03 — P1: Configuration exists but is not consistently consumed or validated

**Evidence:** `generate_answer` sends `timeout=120`; a probe with `Settings(request_timeout_seconds=7)` still observed 120. `Settings.from_env` supports only selected fields: dataset/storage paths, embedding model, chunking, RRF, BM25, and batch size are not exposed through this loader. Streamlit hardcodes slider default 4 while `Settings.answer_top_k` is 6. `rrf_constant` is not validated, so a value of -1 can produce division by zero at rank 1. Thresholds and timeout lack complete finite/range checks; invalid boolean environment strings silently become false. Q1's wrapper does not forward configured overlap.

**Future action:** Use the configured request timeout; document and consistently implement defaults → environment → explicit arguments. Add selected path/model/chunking/index controls without requiring source edits. Validate finite values, integer counts, positive RRF denominator, threshold ranges, and booleans. Derive UI defaults from resolved settings and pass overlap in Q1's wrapper.

**Acceptance:** Captured HTTP requests use the chosen timeout/model/budgets. CLI, UI, snippets, and package use the intended defaults. Invalid settings fail before index access/inference. A custom storage location directs chunks, BM25, Chroma, and manifest coherently.

### V2-04 — P1: Generation budgets and answer validation remain partial

**Evidence:** `_select_context` counts source blocks but not their separators: a 202-character budget produced 209 characters in a two-source probe. It stops when the first non-fitting block is encountered, and can return no context although later smaller blocks fit. Prompt, query, allow-list and output tokens are not jointly budgeted against `num_ctx`. `generate_answer` ignores generation completion/truncation metadata and assumes response shape. A single allowed citation permits additional uncited or unsupported claims. Public-health tone is prompted rather than enforced by a separate runtime policy. `RAGResponse` lists retrieved and quarantined IDs but not the final context selection.

**Future action:** Count complete serialized context; specify a predictable selection policy and total prompt budget. Handle truncated and malformed model responses explicitly. Distinguish citation syntax/ID validity from claim coverage and semantic support. Add a proportionate validation policy or accurately document the remaining prompt-only controls. Keep safe operational errors distinct from actual insufficient-evidence abstention.

**Acceptance:** Context respects its stated bound; omitted evidence cannot be cited; truncation is never silently described as a complete successful answer; malformed responses fail clearly. Tests exercise a valid generation response, an uncited additional claim under the chosen policy, transport failure, and output truncation. Trace can identify which evidence was actually supplied if that feature is claimed.

### V2-05 — P1: Demo evidence needs defensible outcome labels and exact output provenance

**Evidence:** Demo 7 calls the district-log/laboratory-checklist comparison a “correct abstention,” but golden item g09 labels the same task answerable and supplies both relevant chunks. Inspecting those chunks confirms that the corpus contains the log and checklist. Demo 8 is likewise labeled answerable by g11. Abstaining may be conservative given the retrieved context, but it is not a successful answerability result for the whole corpus. Demo 4 acknowledges an output-token limit while the record presents a cleaned answer and separate citation list. This review cannot establish that all displayed prose is verbatim output. Model name and chunk count are recorded, but exact per-run configuration, full context selection, completion metadata, and raw responses are absent.

**Future action:** Distinguish correct out-of-domain/policy abstention from failure to answer an answerable corpus question. Retain failures honestly; investigate retrieval/context selection for comparisons. Store exact answers and citations with reproducible settings, corpus/content version and relevant trace. Recapture a complete second multi-citation success if the existing token-limited record cannot substantiate it.

**Acceptance:** Ten faithful output records include at least two justified abstentions and two complete, source-supported multi-citation answers. Every outcome label is consistent with corpus evidence and the golden set. Do not count g09/g11 failures as unanswerable-question successes. No screenshots/video work is included in this acceptance gate.

### V2-06 — P1: Q3 scorer and orchestration have unresolved result-contract gaps

**Evidence:** `faithfulness_check` now handles non-finite scores and common request/JSON errors, which is an improvement. It still casts booleans/numeric strings to floats, clamps out-of-range values, ignores `unsupported_claims`, and does not compute support from validated claim decisions. A mocked `{"score": true, "unsupported_claims": ["unsupported assertion"]}` returns **1.0**. Exact abstention returns 1.0, mixing abstention with faithfulness. Evidence has no explicit size bound and the client/settings remain hardcoded.

`run_agents` repeats the same query when refinement is absent or unchanged: a probe made three identical retrieval calls. Retry and faithfulness threshold arguments are not validated. Malformed verifier field types and provider exceptions are not normalized. Query screening detects a limited set of injection phrases, not general personal-medical intent. Root, Q3 and Q4 injection patterns differ; some Q3 patterns are absent from runtime. Quarantine history accumulates IDs but is not consistently returned by every failure path. Mixed answer/fallback semantics differ from Q2.

**Future action:** Define strict verifier/judge schemas, including approved-ID lists and finite numeric score rules; preferably compute support from validated per-claim verdicts. Evaluate abstention separately. Inject the judge client/configuration, bound its evidence, and define failure outcomes. Stop no-progress retries, validate limits, normalize response fields, and label optional safety policy extensions honestly.

**Acceptance:** Boolean/out-of-range/malformed or contradictory judge responses cannot pass. Unsupported claims, timeout, invalid verifier IDs/types, no refinement, mixed fallback, and negative/invalid retry settings have deterministic results. Approved-evidence enforcement remains intact. The snippet and PDF describe the same minimal behavior; production features remain explicitly optional.

### V2-07 — P1: Golden-set evaluation is present but not fully specified

**Evidence:** The 18 items have category, facts, answerability and existing chunk IDs. No per-item tuning/held-out split is assigned; the addendum says it should be selected. Versioning names the corpus count but does not bind the set to a content hash. All three adversarial cases are malicious user queries, not clean questions paired with poisoned retrieved passages—the threat specifically emphasized by Q3. No independent annotation evidence is recorded. `load_golden_set` validates only that items is a nonempty list; metrics silently skip answerable items without gold IDs. MRR is truncated at k in code, whereas the prose does not label it MRR@k.

**Future action:** Audit expected facts and evidence sufficiency, not just ID existence. Freeze a stratified tuning/held-out split; record annotation status without claiming independent review that has not happened. Tie references to a content snapshot and add retrieved-passage injection fixtures with clean controls. Specify MRR@k versus full-ranking MRR. Validate item IDs/schema/cohorts and report invalid or excluded items.

**Acceptance:** 15–20 usable questions remain, with explicit splits and evidence provenance. Tests distinguish multi-evidence recall, hit rate, truncated reciprocal rank, abstention, and retrieved-text attacks. A baseline runner/report is a useful optional enhancement; a running MLflow service is not required by the assignment. Targets remain proposed until measured and small-cohort counts/limitations are reported.

### V2-08 — P1: Q4 can retrieve an empty refinement and does not fulfill its failure contract

**Evidence:** `route_after_verification` checks only `refined_query != active_query`; an empty string satisfies that condition for an ordinary question. An injected verifier returning only `{"verdict":"insufficient"}` caused retrieval calls with `['question', '']`. Invalid approved IDs with a “sufficient” verdict can fall through to retry. `verification_node` assumes mapping/list-shaped results; malformed types can raise exceptions or interpret strings as ID sequences. Provider exceptions propagate despite the PDF describing explicit state outcomes. `run_graph` does not expose k; `retrieval_node` defaults to 4. The state retry setting and router argument duplicate the same policy, and `verify_node` is assigned twice.

The all-filtered branch synthesizes the existing query and abstains on no progress. That is a reasonable safe stop, but the PDF's table promises refinement when retries remain. The PDF also says malformed schemas become “insufficient” on page 2 and malformed verdicts abstain on page 3. Raw query text is retained in trace despite the redaction-oriented failure section.

**Future action:** Require a nonempty, changed refinement and valid verdict/schema before retry. Choose an explicit invalid-approved-ID policy. Define no-safe/no-progress stops, typed failure outcomes and trace privacy rules consistently. Expose top_k, validate integer retry bounds, use one authoritative retry setting, and remove the duplicate alias. Document the mapping adapter needed between Q2 `RetrievedChunk` objects and snippet dictionaries; full graph integration is optional.

**Acceptance:** Deterministic tests cover successful answer, valid refinement, missing/empty/repeated refinement, mixed/all-filtered injection, malformed schemas/IDs, unsafe verdict, provider timeout and retry exhaustion. No empty query reaches Retriever; default attempts stay at most three. Write-up and code agree about each terminal path.

### V2-09 — P2: Index manifests do not guarantee compatible or recoverable indexes

**Evidence:** Embedding failures now leave the old collection intact. Failures during collection creation/addition, BM25 save, or manifest save still occur after deletion of the old collection and can leave inconsistent artifacts. The manifest hashes chunk IDs only, so edits that retain IDs are invisible. It omits source content/chunking settings/model revision and is never checked by `HybridRetriever`. Candidate count is not bounded to collection size; empty/small collections and filtered-result counts lack focused tests.

**Future action:** Build replacement stores under a versioned location and activate only after consistency validation. Hash content/provenance as well as IDs and persist effective build parameters. Validate matching stores and embedding configuration on load. Define empty/small-index behavior. Avoid removing published data or indexes as part of unrelated cleanup.

**Acceptance:** An injected failure during vector insertion or BM25 persistence leaves the previous usable build available. Same-ID content changes invalidate the manifest. Mismatched stores/models fail clearly. This is reliability hardening beyond the assignment's minimal indexing requirement, but necessary before claiming safe rebuilds.

## 6. Structure, classes and parameterization direction

The existing `Settings`, `Chunk`, `RetrievedChunk`, `BM25Index`, `HybridRetriever`, and `MalawiRAG` provide a reasonable small-project structure. Keep pure normalization, chunking, citation and metric helpers as functions. Avoid adding classes solely to increase object orientation.

| Boundary | Recommended responsibility | Priority |
| --- | --- | --- |
| Settings | Complete validated configuration; consistent loader and explicit overrides | Fix V2-03 first. |
| Local model client | HTTP request, timeout, response schema/completion metadata; injectable transport | Small useful extraction for Q2 generation and Q3 judge. |
| Answer generator | Context selection, prompt, citation/answer contract | Keep one policy implementation; service class only if it simplifies client injection. |
| Retriever interface | `retrieve` and evidence-gating contract with injectable embedding/vector/BM25 dependencies | Enables offline retrieval tests; retain `HybridRetriever` as implementation. |
| Index builder | Build lifecycle, content manifest, version activation | Encapsulate when implementing failure-safe replacement. |
| Typed verdict/results | Verdict enum, approved IDs, missing facts, failure reason, context provenance | Prefer over loosely typed dictionaries at integration boundaries. |
| MalawiRAG | Coordinate injected retrieval and answering policies | Already partially injected; formalize narrow interfaces rather than adding inheritance. |
| Assignment snippets | Short standalone explanations or explicit root-package adapters | Keep Q3/Q4 design status clear; avoid divergent safety policies without explanation. |
| Packaging | Root source is canonical; reproducible copy/checksum check | Current compared copies match; automation is preventive improvement. |

Keep the Q2-required root entry points and per-task shared directories. A future packaging script or graph adapter is optional. An optional config file should not be added until there is a concrete need; environment and explicit arguments can be sufficient.

## 7. Verification performed and limits

- Read the assignment directly from DOCX XML; read v1 and the agent record, root modules/entry points/tests, Q1/Q3/Q4 snippets, demo records and evaluation artifacts.
- Extracted text from all three required PDFs: Q1 two pages, Q3 three pages, Q4 three pages. Inspected DOCX companion text for corresponding stale claims. No layout/render QA was performed in this review.
- Root suite: **12 passed**. Packaged Q2 suite: **12 passed**. These are equivalent copies, not 24 distinct tests. Runs disabled bytecode and pytest cache writes.
- Executed temporary in-memory/mocked probes for chunking, timeout usage, context budgeting, Q3 judge validation and Q3/Q4 refinement behavior. No real model responses were generated by these probes.
- Counted stored chunks and checked all golden-set chunk IDs against JSONL. Inspected g09's evidence text. Compared the listed canonical/package text and source files; did not audit every binary index file for parity.
- Did not call live Ollama, launch Streamlit, download models, reinstall dependencies, rebuild indexes, or run a full semantic evaluation. Existing demo records are historical evidence, not fresh runtime validation.
- Did not change implementation, assignment outputs or v1. Only this review and append-only agent-record entries are part of this task.

## 8. Suggested implementation order after authorization

1. Fix confirmed chunking, timeout/configuration, Q4 empty-query and Q3 judge-contract defects with targeted regressions.
2. Resolve answer-budget/truncation behavior and typed verifier failures.
3. Rebuild and synchronize artifacts only if chunking/index content changes; update content versions and gold references.
4. Audit/freeze evaluation annotations and capture exact Q2 outputs with corrected outcome labels.
5. Reconcile Q1/Q3/Q4 PDFs, DOCX companions, Q2 design text, settings documentation and agent status claims.
6. Validate root/package parity, meaningful failure cases, documented clean setup and local end-to-end generation. Record what actually ran.
7. Consider failure-safe index activation and additional interfaces as scoped reliability improvements.

## 9. Completion checklist for a future pass

- [ ] V2-01: required written deliverables match current behavior and metric definitions.
- [ ] V2-02: chunk size, overlap and source coverage invariants hold.
- [ ] V2-03: effective configuration is validated and consumed consistently.
- [ ] V2-04: generation budgets, completion status and answer contract are explicit.
- [ ] V2-05: ten exact demo records have defensible labels and required successful examples.
- [ ] V2-06: Q3 judge/orchestration contracts reject malformed and unsupported outcomes.
- [ ] V2-07: golden annotations, splits, content version and retrieved-text attack fixtures are documented.
- [ ] V2-08: Q4 refinement/schema/failure routes match the write-up.
- [ ] V2-09: index recovery/compatibility improvement is implemented or explicitly retained as a limitation.
- [ ] Final validation distinguishes tests, measured model behavior and planned extensions.

Q2 screenshots/video are intentionally outside this checklist.

## 10. Review activity log

### 2026-09-14 — v2 reassessment completed

Created a new review from assignment text, current code, submitted artifacts, passing existing tests, and focused failure probes. Recognized prior fixes, reopened only evidenced residual issues, and separated assignment corrections from engineering hardening. No implementation changes were made.

### 2026-09-14 — v2 implementation pass

- **Completed:** Applied runtime fixes for configured HTTP timeouts, validated
  RRF/evidence thresholds, bounded context accounting, chunk overlap handling,
  Q1 overlap propagation, UI defaults, Q3 judge validation/no-progress retries,
  and Q4 refinement validation/top-k injection.
- **Completed:** Synchronized root and Q2 package modules, refreshed Q2 design
  statistics and demo outcome labels, reran ingestion, and added regression tests.
- **Validation:** Root tests pass; package tests are rerun after synchronization.
  The embedding index rebuild was attempted with the cached local model but was
  interrupted after prolonged CPU execution; existing index artifacts remain in
  place and should be rebuilt in a normal local runtime before release.
- **Pending:** Required Q1/Q3/Q4 PDF/DOCX companions still need regeneration to
  remove stale prose and metric definitions. Golden-set split/annotation audit,
  failure-safe index activation, and clean-install/live end-to-end validation
  remain open. Q2 screenshots/video remain explicitly deferred.

### 2026-09-14 — Documentation correction pass

- **Completed:** Updated Q1 retrieval PDF/DOCX to report the current 1,036 chunks
  and 4,868-character maximum, with the six-chunk operating point. Updated Q3
  PDF/DOCX Recall@4 wording to distinguish set-based recall from Hit@4. Refreshed
  both Q2 design copies and corrected answerable-comparison labels in both demos.
- **Validation:** Active documentation no longer contains superseded 787, 1,593,
  2,663, or four-chunk statements outside historical review logs. DOCX rendering
  was attempted with the prescribed renderer; `soffice` is unavailable here, so
  visual Word QA could not run.
