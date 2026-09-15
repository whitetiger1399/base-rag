from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Flowable, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer


OUT = Path("shared_output/Q2_RAG_Demo/docs/RAG_FLOW_EXPLAINED.pdf")


class FlowDiagram(Flowable):
    def __init__(self):
        super().__init__()
        self.width, self.height = 7.0 * inch, 2.0 * inch

    def draw(self):
        c = self.canv
        labels = ["Excel rows", "Chunking", "Indexes", "Hybrid retrieval", "Ollama answer"]
        w, h, gap = 1.18 * inch, 0.48 * inch, 0.48 * inch
        y = 1.25 * inch
        for i, label in enumerate(labels):
            x = 0.03 * inch + i * (w + gap)
            c.setFillColor(colors.HexColor("#E8F1FA")); c.setStrokeColor(colors.HexColor("#2F5D8A"))
            c.roundRect(x, y, w, h, 7, fill=1, stroke=1)
            c.setFillColor(colors.HexColor("#17324D")); c.setFont("Helvetica-Bold", 7)
            parts = label.split(" ")
            if len(parts) > 2:
                c.drawCentredString(x + w / 2, y + h / 2 + 4, " ".join(parts[:2]))
                c.drawCentredString(x + w / 2, y + h / 2 - 6, " ".join(parts[2:]))
            else:
                c.drawCentredString(x + w / 2, y + h / 2 - 2, label)
            if i < len(labels) - 1:
                c.setStrokeColor(colors.HexColor("#6B7280"))
                end = x + w + gap - 0.08 * inch
                c.line(x + w, y + h / 2, end, y + h / 2)
                c.line(end, y + h / 2, end - 5, y + h / 2 + 4)
                c.line(end, y + h / 2, end - 5, y + h / 2 - 4)
        c.setFillColor(colors.HexColor("#FFF4D6")); c.setStrokeColor(colors.HexColor("#B7791F"))
        c.roundRect(2.05 * inch, 0.25 * inch, 2.9 * inch, 0.45 * inch, 7, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#6B4E00")); c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(3.5 * inch, 0.49 * inch, "Evidence gate → cited answer or cannot find in sources")
        c.setStrokeColor(colors.HexColor("#B7791F")); c.line(3.5 * inch, y, 3.5 * inch, 0.7 * inch)


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Cover", parent=styles["Title"], fontSize=24, leading=29, textColor=colors.HexColor("#17324D"), alignment=TA_CENTER, spaceAfter=14))
styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=11, leading=15, textColor=colors.HexColor("#4B5563"), alignment=TA_CENTER, spaceAfter=14))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontSize=16, leading=20, textColor=colors.HexColor("#17324D"), spaceBefore=8, spaceAfter=7))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontSize=9.2, leading=13, spaceAfter=6))
code_style = ParagraphStyle("Code", fontName="Courier", fontSize=7.5, leading=10, backColor=colors.HexColor("#F3F4F6"), borderColor=colors.HexColor("#D1D5DB"), borderWidth=.5, borderPadding=7, spaceBefore=3, spaceAfter=7)


def code(value):
    return Preformatted(value.strip("\n"), code_style)


def h(value):
    return Paragraph(value, styles["H1x"])


def p(value):
    return Paragraph(value, styles["Bodyx"])


def footer(canvas, doc):
    canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#D1D5DB")); canvas.line(.65*inch, .55*inch, 7.85*inch, .55*inch)
    canvas.setFont("Helvetica", 7.5); canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawString(.65*inch, .36*inch, "Malawi Public Health RAG • Q2 learning guide")
    canvas.drawRightString(7.85*inch, .36*inch, f"Page {doc.page}"); canvas.restoreState()


story = [
    Spacer(1, .65*inch), Paragraph("How the Malawi RAG Works", styles["Cover"]),
    Paragraph("A step-by-step guide from workbook rows to a cited local Ollama answer", styles["Sub"]),
    FlowDiagram(), Spacer(1, .2*inch),
    p("This guide follows the current Q2 implementation. Each stage shows its input, transformation, output, and the file responsible for it."),
    p("Current corpus: six Malawi IDSR workbooks, 1,036 retrieval chunks, local all-MiniLM-L6-v2 embeddings, and local Ollama qwen3:8b generation."),
    PageBreak(),
    h("1. Configuration and workbook input"),
    p("<b>Files:</b> <font name='Courier'>src/config.py</font> and <font name='Courier'>Task2_dataset1/MWTGBookletsExcel/*.xlsx</font>. Settings contains model names, paths, chunk sizes, thresholds, timeouts, and the default batch limit."),
    code('Settings(\n  embedding_model="sentence-transformers/all-MiniLM-L6-v2",\n  ollama_model="qwen3:8b",\n  ollama_url="http://127.0.0.1:11434",\n  answer_top_k=6,\n  batch_max_questions=10\n)'),
    p("A workbook row starts as a paragraph number plus paragraph text:"),
    code('paragraph number: 450\ntext: "Reduce exposures to infectious or environmental hazards..."'),
    h("2. Structure-aware chunking"),
    p("<b>File:</b> <font name='Courier'>src/chunking.py</font>. Empty rows are skipped, whitespace is normalized, headings are detected, and related rows are merged inside a section. A heading such as <font name='Courier'>6.3.11 Reduce exposures...</font> becomes the active section. Oversized rows are split at sentence boundaries."),
    code('Rows 450–452\n450: Reduce exposures...\n451: Use protective equipment...\n452: Improve ventilation...\n        ↓\nsection: 6.3.11 Reduce exposures...\nparagraph_start: 450\nparagraph_end: 452'),
    p("TG Booklet 3 has approximately 2,064 source entries and produces 213 retrieval chunks. The rows are merged to reduce fragmentation, while their paragraph range and section metadata preserve provenance."),
    h("3. Chunk identity and storage"),
    p("Each chunk receives a stable ID and metadata before it is written to <font name='Courier'>storage/chunks.jsonl</font>."),
    code('{\n  "chunk_id": "TG_Booklet_3:p411-p413:c0043",\n  "section": "Annex 4A: District log...",\n  "topic": "District log of suspected outbreaks and alerts",\n  "paragraph_start": 411, "paragraph_end": 413,\n  "text": "Section: Annex 4A...\\nRecord verbal or written..."\n}'),
    PageBreak(),
    h("4. Embedding vectors and ChromaDB"),
    p("<b>File:</b> <font name='Courier'>src/indexing.py</font>. Every chunk text is encoded by all-MiniLM-L6-v2. Text is transformed into a numeric vector representing semantic meaning."),
    code('"Community members report unusual health events."\n        ↓ MiniLM encoder\n[0.12, -0.44, 0.73, ...]'),
    p("The normalized vectors, original text, IDs, and metadata are stored in a persistent Chroma cosine collection. The query is encoded by the same model during retrieval."),
    h("5. BM25 lexical index"),
    p("<b>File:</b> <font name='Courier'>src/bm25.py</font>. BM25 tokenizes text, counts term frequency, accounts for document length, and rewards rare exact terms. It is strong for disease names, acronyms, laboratory terms, and exact wording."),
    code('Query: "Chikungunya PCR"\nTokens: ["chikungunya", "pcr"]\nHigh score: a chunk containing both exact terms'),
    p("BM25 uses the same chunk IDs as ChromaDB, allowing both rankings to be combined safely."),
    h("6. HybridRetriever and RRF"),
    p("<b>File:</b> <font name='Courier'>src/retrieval.py</font>. HybridRetriever runs semantic vector search and BM25 search, applies filters, and combines their rankings with Reciprocal Rank Fusion."),
    code('Question\n"How do communities report unusual health events?"\n\nVector search → semantic ranking\nBM25 search   → exact-term ranking\nRRF(d)        = Σ 1 / (60 + rank(d))'),
    code('RetrievedChunk(\n  chunk_id="TG_Booklet_1:p86-p89:c0022",\n  rank=1, semantic_similarity=0.72,\n  bm25_score=8.41, hybrid_score=0.031\n)'),
    PageBreak(),
    h("7. Evidence gate and safety filter"),
    p("<b>Files:</b> <font name='Courier'>src/rag.py</font>, <font name='Courier'>src/guardrails.py</font>, and the Q3 reference snippet. Untrusted text is normalized for Unicode, invisible-character, homoglyph, leetspeak, punctuation, and spacing tricks. Word-preserving and compact regex checks run first; a replaceable local semantic detector can identify injection intent beyond fixed patterns."),
    code('"iɢnore pr3vious instruc✱ions"\n        ↓ security-only normalization\n"ignore previous instruc ions"\n        ↓ compact + semantic screening\nquarantine unsafe chunk by ID\n        ↓\nuse verifier-approved evidence only'),
    p("A separate embedding-similarity gate can reject topically weak evidence before the LLM verifier. Structured audit events record the detection layer, chunk ID, retry, similarity score, cited IDs, and faithfulness score without logging malicious passage text. Detector or schema failures fail closed."),
    h("8. Context construction and local Ollama"),
    p("<b>File:</b> <font name='Courier'>src/generation.py</font>. Complete source blocks are selected and placed in a bounded prompt. The model sees the question plus source text labelled as untrusted reference data."),
    code('SOURCE [TG_Booklet_1:p86-p89:c0022]\nSection: Community Based Surveillance\nParagraphs: 86-89\nCONTENT (untrusted reference text):\nCommunity members report unusual events...'),
    code('POST http://127.0.0.1:11434/api/chat\n{ "model": "qwen3:8b", "stream": false,\n  "messages": [system_prompt, question_and_sources] }'),
    p("The prompt requires answers only from supplied evidence, a general public-health tone, and exact bracketed chunk citations."),
    h("9. Citation validation and response"),
    code('Valid:   "Community reporting uses trained members. [TG_Booklet_1:p86-p89:c0022]"\nInvalid: "Prevalence is 40%. [invented:id]"\nResult:  valid answer or "cannot find in sources"'),
    p("The validator rejects missing, malformed, unknown, or omitted-source citations. The CLI and Streamlit trace can show rank, semantic score, BM25 score, hybrid score, section, paragraph range, and source text."),
    h("10. Batch submission output"),
    p("<b>File:</b> <font name='Courier'>batch_submit.py</font>. The runner reads the configured first 10 questions from Test.csv and writes four SampleSubmission-format rows per question: keywords, paragraph numbers, answer, and reference document."),
    code('test_submission_2026_09_14_15_48_38.csv\nQ4_keywords\nQ4_paragraph(s)_number\nQ4_question_answer\nQ4_reference_document'),
    p("The filename is timestamped automatically. The CSV is flushed after each completed question, and the terminal shows a compact line such as <font name='Courier'>Processing test question 4/10 (40.0%) — Q10</font>."),
    h("11. Three-question Ragas evaluation"),
    p("Ragas separates evidence retrieval from answer generation. On Q220, Q1016, and Q1226, context precision and context recall were 1.0000 for every question. Mean faithfulness was 0.8333, answer relevancy 0.8665, answer correctness 0.9481, and answer similarity 0.8756."),
    code('Metric              Q220    Q1016   Q1226   Mean\nFaithfulness         0.5000  1.0000  1.0000  0.8333\nAnswer relevancy     0.8132  1.0000  0.7861  0.8665\nContext precision    1.0000  1.0000  1.0000  1.0000\nContext recall       1.0000  1.0000  1.0000  1.0000\nAnswer correctness   0.9866  0.9642  0.8933  0.9481\nAnswer similarity    0.9465  0.8570  0.8232  0.8756'),
    p("Q220 shows why correctness does not replace grounding: it closely matched the reference but received 0.5000 faithfulness. This is a small development sample, not a held-out production benchmark. Local qwen3:8b generated and judged the answers, so human review remains necessary. The sample was kept at three because sustained inference caused significant MacBook heat, a machine resource constraint rather than an observed algorithm failure."),
    h("End-to-end transformation"),
    code('Excel rows → section-aware chunks → JSONL metadata\n→ embedding vectors in ChromaDB + BM25 terms\n→ query vector + lexical search → RRF ranking\n→ safety/evidence gate → bounded Ollama prompt\n→ citation validation → grounded answer or abstention'),
]

OUT.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(str(OUT), pagesize=letter, rightMargin=.65*inch, leftMargin=.65*inch, topMargin=.65*inch, bottomMargin=.72*inch, title="How the Malawi RAG Works")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
