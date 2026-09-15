# Local Ragas evaluation setup

Status: a live three-question local Ragas evaluation was completed and reviewed
on 2026-09-15. It is a small development sample used to validate the evaluation
method and understand the RAG system's behavior. It is not a held-out or
production-scale quality claim. The sample size was deliberately limited because
sustained local Qwen inference caused significant heat on the MacBook; this is a
machine resource constraint, not evidence of an algorithm failure.

## Why this project uses Ragas

A RAG answer can sound fluent while failing at different stages. Retrieval may
miss the evidence, the model may ignore good evidence, or the answer may add an
unsupported claim. One overall accuracy number cannot locate that failure.
Ragas evaluates the retrieval and generation stages separately using the saved
question, reference answer, exact retrieved contexts, and generated answer.

For this project, Ragas is useful because it:

- tests whether the answer is supported by the Malawi IDSR source chunks;
- distinguishes retrieval quality from answer-generation quality;
- compares generated answers with labeled `Train.csv` references;
- produces repeatable per-question diagnostics for regression testing; and
- complements deterministic checks such as citation validity, Recall@k, MRR,
  safety tests, and abstention tests rather than replacing them.

The evaluator uses local `qwen3:8b` as both answer model and Ragas judge, so
scores can contain correlated self-evaluation bias. The current hash-selected
smoke subset is also not held out. These results are suitable for development
diagnosis, not an independent quality claim.

## Run from the repository root

Activate your existing environment and install the pinned requirements if needed:

```bash
source rag-setup/bin/activate
python -m pip install -r requirements.txt
```

Ensure Ollama is already running with `qwen3:8b` installed. If necessary, start it in a separate terminal with `ollama run qwen3:8b`. Then run:

```bash
rag-setup/bin/python evaluate_ragas.py
```

The script reads `evaluation_config.json`. Change `max_questions` there (default **10**), rather than adding a terminal question-count parameter. The batch submission limit is independent.

Alternatively, from `shared_output/Q2_RAG_Demo`, using the existing root environment:

```bash
../../rag-setup/bin/python evaluate_ragas.py
```

That copy is self-contained and uses its own `evaluation_config.json`, sources, datasets, and indexes. When sharing Q2 alone, create an environment there and use `python evaluate_ragas.py`.

## Inputs and selection

The script uses labeled `Task2_dataset1/Train.csv` (748 records observed when planning), validates IDs and required fields, and selects a reproducible hash-ordered subset using seed 42. Selected IDs are saved in each run manifest. This is explicitly a development smoke subset, not a stratified or held-out test set.

`Test.csv` has questions without reference answers. `SampleSubmission.csv` specifies four target fields per ID and is not ground truth. Timestamped submission CSVs do not capture exact generation contexts. They are not passed to supervised metrics by this script. Historical format/coverage auditing and reference-free scoring are separate future work; historical faithfulness needs matching context traces.

## Metrics

All six outputs are interpreted on a 0-to-1 scale, where a larger value is
better for that metric. They are diagnostics, not calibrated probabilities.

| Output name | Inputs | What it tests | How to read it |
|---|---|---|---|
| `faithfulness` | Answer + exact safe generation contexts | Whether answer claims are supported by supplied evidence | Low score with high correctness can mean the answer matches the reference but contains claims the retrieved context does not support clearly. |
| `answer_relevancy` | Question + answer | Whether the response directly addresses the question | It does not prove factual correctness or grounding. |
| `context_precision` | Question + ordered retrieved contexts + reference | Whether relevant evidence appears early and irrelevant context is limited | High precision can coexist with low recall if only a small part of the required evidence was retrieved. |
| `context_recall` | Retrieved contexts + reference | Whether retrieved evidence covers the facts in the reference | It tests evidence coverage, not final-answer wording. |
| `answer_correctness` | Answer + reference | Reference-based factual and semantic quality | In Ragas 0.1.21 the default combines 0.75 factuality and 0.25 semantic similarity. |
| `answer_similarity` | Answer + reference embeddings | Semantic closeness to the reference answer | Similar wording or meaning is not by itself proof of factual correctness. |

Application generation settings remain unchanged. Retrieval metrics receive full retrieved contexts; faithfulness receives only contexts selected for generation. Faithfulness for abstentions is marked not applicable. Other metric errors/undefined values remain explicit errors, not zero or perfect scores. Summaries include valid/selected counts, errors, and not-applicable counts. Existing deterministic retrieval helpers in `src/evaluation.py` remain separate from this runner.

## Three-question evaluation sample

The evaluation uses the three questions in run `20260915T005831373201Z` that
have a complete set of all six Ragas metrics. Together they provide 18 successful
metric records. The evaluator used Ragas 0.1.21, local `qwen3:8b`, the saved
reference answers, and the exact retrieved/generation contexts.

| Question ID | Short result | Faithfulness | Answer relevancy | Context precision | Context recall | Answer correctness | Answer similarity | State |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `Q220` | Correctly identifies the national level | 0.5000 | 0.8132 | 1.0000 | 1.0000 | 0.9866 | 0.9465 | Complete |
| `Q1016` | Correctly says routine confirmation is not required | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9642 | 0.8570 | Complete |
| `Q1226` | Explains immediate, weekly, and monthly reporting | 1.0000 | 0.7861 | 1.0000 | 1.0000 | 0.8933 | 0.8232 | Complete |

For the three evaluated questions, the means are: faithfulness
0.8333, answer relevancy 0.8665, context precision 1.0000, context recall
1.0000, answer correctness 0.9481, and answer similarity 0.8756.

The sample shows why multiple metrics are needed. `Q220` has near-perfect
answer correctness and similarity but faithfulness of 0.5, so matching the
reference does not guarantee that every generated claim was judged supported by
the supplied contexts. `Q1016` is the strongest balanced example. `Q1226` is
fully grounded but has lower answer relevancy and similarity, suggesting that a
concise answer more closely aligned with the question/reference could improve
generation quality without changing retrieval.

Do not compare raw means without their three-question sample size, and do not
average the six metric types into one score. Review `answers.jsonl` and
`judge_calls.jsonl` before treating an unexpectedly low score as an application
defect; the trace may reveal an answer-claim boundary or ambiguous reference.
Larger evaluation runs can be scheduled later on hardware suited to sustained
local inference.

## M1 / 16 GB resource behavior

One process runs one question and one metric at a time. The direct async Ragas metric API avoids the older bulk executor's Python 3.9 semaphore issue without monkeypatching it. Judge completions are requested sequentially; no multiprocessing pool is created. CPU threads are capped at two, embeddings use CPU with batch size eight, and judging reuses local Qwen. No hosted API key is used.

Keep other batch/interactive model requests idle during evaluation. The output-directory lock prevents another evaluator using that directory, but cannot prevent unrelated clients from calling Ollama. For stricter server limits, configure `OLLAMA_NUM_PARALLEL=1` and `OLLAMA_MAX_LOADED_MODELS=1` in the environment that launches Ollama, then restart it yourself when appropriate. Exporting variables in a client terminal does not change an already-running macOS server.

The initial judge configuration is 8,192 context tokens and 1,024 output tokens. This differs from the plan's 4,096-token pilot suggestion to leave more space for Ragas prompts, but is **not hardware-benchmarked**. The Qwen tokenizer counts the chat-formatted input, with 128 tokens reserved for template differences. The `judge_tokenizer` config defaults to `Qwen/Qwen3-8B`; the first run downloads tokenizer files only (not model weights). Set `tokenizer_local_files_only` to true after caching if offline execution is required. Keep the tokenizer aligned with the configured Ollama model. Actual overflow is recorded as a metric error without truncating sources. Baseline application context/output limits are never reduced by the evaluator.

HTTP timeout is 300 seconds; metric timeout is 900 seconds. On a transport timeout, the run stops rather than immediately submitting more work while Ollama may still be processing. Context, parsing, and undefined-score errors are printed and recorded while subsequent metrics continue. They do not trip the infrastructure stop. Inspect server readiness and logs before resuming. Exact latency and memory requirements remain unmeasured.

## Outputs and resume

Each run writes a UTC-stamped directory under `shared_output/Q2_RAG_Demo/evaluation/` (or local `evaluation/` in the standalone package):

- `manifest.json`: selected IDs, application/config values, input/code/index fingerprint, model digest, status.
- `answers.jsonl`: one durable answer checkpoint before judge calls, with exact contexts and retrieved metadata.
- `metrics.jsonl`: appended and flushed result per metric, including explicit errors.
- `judge_calls.jsonl`: prompts and raw judge responses for debugging.
- `scores.csv`, `summary.json`, `report.md`: progressively refreshed score outputs.

To resume, use the exact run directory printed at startup:

```bash
rag-setup/bin/python evaluate_ragas.py --resume shared_output/Q2_RAG_Demo/evaluation/YOUR_RUN_DIRECTORY
```

Saved answers and successful/not-applicable metrics are reused; failed metrics are retried. Input/config/code fingerprints and model digest must match. After changing settings, start a new run. Interrupted trailing JSONL fragments are removed on resume; completed entries are preserved.

A completed smoke run is not evidence of full-model quality. Inspect score coverage, abstentions, raw answers, judge errors, and reference-label quality. Qwen evaluating its own answers can have correlated bias. Publish actual values with the manifest and sample size only after running and reviewing the results.

## 2026-09-15 — Corrected false infrastructure failures

Saved run errors showed the previous UTF-8 byte budget rejected prompts before
Ollama was called. This was an evaluator bug, not evidence of insufficient RAM.
The corrected setup uses Qwen token counts, reuses the retriever's MiniLM model
through a nondeprecated adapter, and keeps all inference sequential. No extra
processes or embedding thread pools are created. Actual transport failures still
stop safely; completed scores remain checkpointed.

Run `rag-setup/bin/python evaluate_ragas.py` from the repository root after this
update. Start a new run because the old resume fingerprint includes the previous
code/configuration. Historical results remain untouched. The root config has
10 questions, while the packaged config currently has 1; use the config belonging
to the script you run. No live evaluation was performed during this fix.

## 2026-09-15 — Answer-generation timeout

`generation_timeout_seconds` now defaults to 600 in evaluation_config.json.
This controls answer generation separately from the 300-second judge HTTP
timeout and 900-second metric deadline. Only transport patience changes; model
prompts and output/context budgets are preserved. Answer transport errors are
saved in errors.jsonl and stop with a concise message. No overlapping retry is
submitted. A longer timeout permits slow inference but does not guarantee Ollama
will finish. Start a new run after updating code/configuration because old resume
fingerprints differ. No live inference was run to validate this change.
