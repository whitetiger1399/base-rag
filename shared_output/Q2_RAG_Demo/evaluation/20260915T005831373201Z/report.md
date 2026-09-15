# Ragas results

Development smoke benchmark; not an independent test score.

Reported evaluation sample: three questions with a complete set of all six
metrics. The sample was kept small because sustained local inference caused
significant MacBook heat; this is a hardware resource constraint rather than an
algorithm failure. See `../../docs/RAGAS_EVALUATION.md` for definitions,
per-question results, interpretation, and limitations.

| Metric | Mean | Valid / selected | Errors | N/A |
|---|---:|---:|---:|---:|
| faithfulness | 0.8333333333333334 | 3/3 | 0 | 0 |
| answer_relevancy | 0.8664602072497581 | 3/3 | 0 | 0 |
| context_precision | 0.9999999999822222 | 3/3 | 0 | 0 |
| context_recall | 1.0 | 3/3 | 0 | 0 |
| answer_correctness | 0.9480607495331528 | 3/3 | 0 | 0 |
| answer_similarity | 0.875576331465944 | 3/3 | 0 | 0 |
