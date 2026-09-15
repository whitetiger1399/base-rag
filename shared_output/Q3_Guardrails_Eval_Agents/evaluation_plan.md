# Q3 Evaluation Addendum

`golden_set.json` is the versioned 18-item set for this submission. It contains
8 single-hop questions, 4 multi-chunk questions, 3 unanswerable questions, and 3
adversarial safety questions. The relevant chunk IDs are tied to the current
1,036-chunk corpus manifest.

For answerable items with a non-empty gold set:

- `Recall@k = |retrieved_top_k ∩ gold_relevant_chunks| / |gold_relevant_chunks|`.
- `Hit@k` is 1 when any gold chunk appears in the top k, otherwise 0.
- `Full-evidence recall` is 1 only when every required chunk appears in the top k.
- `MRR` is the reciprocal rank of the first relevant chunk, averaged across items;
  an item with no relevant result contributes zero.

Unanswerable and adversarial items are excluded from retrieval recall denominators
and are evaluated separately for correct abstention and injection blocking. The
12-item tuning split and six-item held-out split should be selected and frozen
before threshold changes; their assignment is still pending annotation. The helper `src/evaluation.py` computes the retrieval
metrics from ranked chunk IDs and the golden records.

Faithfulness remains a generation-level measure: split an answer into factual
claims, require each claim to have an allowed citation, and score support against
the cited evidence. Report citation validity, citation coverage, claim support,
abstention precision/recall/F1, and injection block/false-positive rates by cohort.
The numeric thresholds in the Q3 PDF are proposed release targets until a labeled
baseline is recorded.

## Ragas evaluation

Ragas complements the deterministic Q3 checks by separating retrieval quality
from generation quality. A fluent answer may still be unsupported, irrelevant,
or based on incomplete evidence. The local evaluator therefore records six
diagnostics: faithfulness, answer relevancy, context precision, context recall,
answer correctness, and answer similarity. These metrics are interpreted
individually; they are not averaged into one composite score.

Three questions with complete metric coverage were evaluated using Ragas 0.1.21,
local Ollama `qwen3:8b`, labeled `Train.csv` references, and the exact contexts
used by the RAG pipeline:

| ID | Faithfulness | Answer relevancy | Context precision | Context recall | Answer correctness | Answer similarity |
|---|---:|---:|---:|---:|---:|---:|
| Q220 | 0.5000 | 0.8132 | 1.0000 | 1.0000 | 0.9866 | 0.9465 |
| Q1016 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9642 | 0.8570 |
| Q1226 | 1.0000 | 0.7861 | 1.0000 | 1.0000 | 0.8933 | 0.8232 |
| **Mean** | **0.8333** | **0.8665** | **1.0000** | **1.0000** | **0.9481** | **0.8756** |

The perfect context precision and recall in this sample indicate that the
retriever supplied strong reference-aligned evidence. Q220 nevertheless scored
0.5 for faithfulness despite 0.9866 answer correctness, demonstrating why Q3
needs claim-to-context grounding checks in addition to reference agreement.
Q1016 was strong across all measures. Q1226 was fully grounded but less concise
and reference-aligned, reflected in its lower relevancy and similarity scores.

This is a small development sample, not a held-out production benchmark. Local
Qwen generated and judged the answers, which can introduce correlated bias, so
human review remains part of the Q3 evaluation design. The sample size was kept
at three because sustained local inference caused significant MacBook heat;
this is a machine resource constraint and not an observed algorithm failure.
