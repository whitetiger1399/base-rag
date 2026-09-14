# Q2 Demo Outputs — Current indexed run

These ten outputs were captured from the local Ollama `qwen3:8b` assistant after
rebuilding the synchronized 1,036-chunk Chroma/BM25 indexes. Trace entries show
the leading retrieved evidence. Screenshots/video remain intentionally deferred.

## 1. Community Based Surveillance

Question: What is Community Based Surveillance?

Answer: Community-Based Surveillance (CBS) is a simple, adaptable, and low-cost
public health initiative managed by communities in coordination with formal
surveillance structures. It involves training and empowering communities and
designated community focal points to monitor potential health risks, notifiable
and seasonal diseases, and signs of disease outbreaks.

Citation: `[TG_Booklet_1:p430-p436:c0086]`

Trace: top result `[TG_Booklet_1:p436-p441:c0087]`, semantic 0.623, BM25 10.165.

## 2. Indicator-based surveillance

Question: What is indicator based surveillance?

Answer: Indicator-based surveillance is the systematic identification,
collection, monitoring, analysis, and interpretation of structured data from
well-identified formal sources. It uses standardized data to monitor diseases,
conditions, and events and assess surveillance performance.

Citations: `[TG_Booklet_1:p77-p82:c0019]` and
`[TG_Booklet_4:p136-p138:c0019]`

Trace: top semantic 0.708; six candidates retrieved. Result: grounded
multi-chunk answer.

## 3. Case-based surveillance

Question: What is case based surveillance?

Answer: Case-based surveillance is the ongoing and rapid identification of
identifiable cases for follow-up. It is used for diseases targeted for
elimination or eradication and during confirmed outbreaks; each case is
reported immediately using a case-based form.

Citation: `[TG_Booklet_1:p77-p82:c0019]`

Trace: top semantic 0.688, BM25 8.208.

## 4. One Health reporting

Question: How should the One Health approach be implemented to improve reporting?

Answer: Strengthen collaboration across health, agriculture, livestock,
environment, immigration, and defence sectors. Share detected events across
relevant sectors, compile facility data, provide regular feedback, and use clear
reporting elements and communication channels.

Citations: `[TG_Booklet_6:p293-p293:c0328]`,
`[TG_Booklet_2:p161-p165:c0020]`, and
`[TG_Booklet_4:p360-p364:c0054]`

Trace: top semantic 0.647; six candidates retrieved. Result: grounded
multi-chunk answer (the observed long run reached the output-token limit after
the fourth supported point).

## 5. Laboratory result review

Question: How can laboratory results be reviewed during an outbreak investigation?

Answer: Discuss laboratory results with the investigation team at the health
facility and check consistency with clinical findings. Seek assistance from
national program managers or technical experts when questions remain.

Citation: `[TG_Booklet_3:p292-p294:c0026]`

Trace: top semantic 0.637, BM25 12.887.

## 6. Rumor logbook

Question: Why is it important to maintain a logbook of rumors?

Answer: It helps track and manage misinformation during public-health
emergencies, identify rumor sources and patterns, and support rapid public
statements or press conferences when damaging rumors spread.

Citation: `[TG_Booklet_3:p1811-p1820:c0186]`

Trace: top semantic 0.398; six candidates retrieved.

## 7. District log versus laboratory checklist

Question: Compare the district log of suspected outbreaks with the laboratory
supplies checklist.

Answer: cannot find in sources

Trace: top semantic 0.680; the evidence gate did not support the comparison.
Result: conservative failure on an answerable comparison; this is retained as
a regression case and does not count as an unanswerable-question abstention.

## 8. Chikungunya versus diabetes confirmation

Question: Compare laboratory confirmation methods for Chikungunya and diabetes.

Answer: cannot find in sources

Trace: the post-generation abstention validator rejected a partial comparison
that contained the abstention phrase. The final returned answer is the exact
required abstention; this is retained as an answerable-query failure case.

## 9. Out-of-domain engine oil

Question: What is the recommended engine oil for a 2025 Formula One car?

Answer: cannot find in sources

Trace: top semantic 0.233. Result: correct out-of-domain abstention.

## 10. Personal medical advice

Question: Can you diagnose my symptoms and prescribe a treatment?

Answer: cannot find in sources

Trace: top semantic 0.361. Result: correct personal-medical-advice abstention.

## Coverage check

The record contains ten observed questions, two grounded multi-citation answers,
and four abstention outcomes. The One Health output is marked as token-limited;
the deterministic validator still requires exact citations and abstains on
mixed answers containing the fallback phrase. Screenshots/video are the only
Q2 deliverable item intentionally left deferred.
