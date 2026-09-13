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
before threshold changes. The helper `src/evaluation.py` computes the retrieval
metrics from ranked chunk IDs and the golden records.

Faithfulness remains a generation-level measure: split an answer into factual
claims, require each claim to have an allowed citation, and score support against
the cited evidence. Report citation validity, citation coverage, claim support,
abstention precision/recall/F1, and injection block/false-positive rates by cohort.
The numeric thresholds in the Q3 PDF are proposed release targets until a labeled
baseline is recorded.
