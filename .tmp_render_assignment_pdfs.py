from pathlib import Path

from docx import Document
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage, LongTable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, TableStyle


JOBS = [
    (
        Path("shared_output/Q1_Retrieval_Design/Q1_Retrieval_Design.docx"),
        Path("shared_output/Q1_Retrieval_Design/Q1_Retrieval_Design.pdf"),
        "Q1 | Retrieval Design",
        None,
    ),
    (
        Path("shared_output/Q3_Guardrails_Eval_Agents/Q3_Guardrails_Eval_Agents.docx"),
        Path("shared_output/Q3_Guardrails_Eval_Agents/Q3_Guardrails_Eval_Agents.pdf"),
        "Malawi Public Health RAG - Q3",
        "3. Multi-agent workflow",
    ),
    (
        Path("shared_output/Q4_Graph_Multi_Agent/graph-based-multi-agent.docx"),
        Path("shared_output/Q4_Graph_Multi_Agent/graph-based-multi-agent.pdf"),
        "Malawi Public Health RAG - Q4",
        "3. Conditional routing and termination",
    ),
]


def iter_blocks(document):
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield DocxParagraph(child, document)
        elif child.tag.endswith("}tbl"):
            yield DocxTable(child, document)


def escape(value):
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")


base = getSampleStyleSheet()
navy = colors.HexColor("#17365D")
blue = colors.HexColor("#1F4E78")
light_blue = colors.HexColor("#DCE6F1")
body = ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=8.8, leading=11.5, textColor=colors.HexColor("#222222"), spaceAfter=5)
title = ParagraphStyle("Title", parent=body, fontName="Helvetica-Bold", fontSize=19, leading=22, alignment=TA_CENTER, textColor=navy, spaceAfter=5)
subtitle = ParagraphStyle("Subtitle", parent=body, fontSize=9, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=5)
meta = ParagraphStyle("Meta", parent=subtitle, fontSize=8, spaceAfter=11)
h1 = ParagraphStyle("H1", parent=body, fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=navy, spaceBefore=8, spaceAfter=5, keepWithNext=True)
h2 = ParagraphStyle("H2", parent=body, fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=blue, spaceBefore=6, spaceAfter=4, keepWithNext=True)
h3 = ParagraphStyle("H3", parent=body, fontName="Helvetica-Bold", fontSize=9.5, leading=11.5, textColor=blue, spaceBefore=5, spaceAfter=3, keepWithNext=True)
cell = ParagraphStyle("Cell", parent=body, fontSize=6.9, leading=8.5, spaceAfter=0)
cell_center = ParagraphStyle("CellCenter", parent=cell, alignment=TA_CENTER)
cell_header = ParagraphStyle("CellHeader", parent=cell, fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_LEFT)


def render(docx_path, pdf_path, footer_label, forced_break_heading):
    source = Document(docx_path)
    story = []
    intro_index = 0
    diagram_specs = {
        "Q1_Retrieval_Design.docx": ("Q1_RETRIEVAL_WORKFLOW.png", 2.18),
        "Q3_Guardrails_Eval_Agents.docx": ("Q3_GUARDRAIL_EVAL_AGENT_WORKFLOW.png", 2.80),
        "graph-based-multi-agent.docx": ("Q4_GRAPH_MULTI_AGENT_WORKFLOW.png", 5.99),
    }
    for block in iter_blocks(source):
        if isinstance(block, DocxParagraph):
            text = block.text.strip()
            if not text:
                if "<w:drawing" in block._p.xml:
                    diagram_spec = diagram_specs.get(docx_path.name)
                    if diagram_spec:
                        diagram = docx_path.parent / diagram_spec[0]
                    else:
                        diagram = None
                    if diagram and diagram.exists():
                        story.extend([
                            RLImage(str(diagram), width=7.0 * inch, height=diagram_spec[1] * inch),
                            Spacer(1, 5),
                        ])
                continue
            style_name = block.style.name
            if forced_break_heading and text == forced_break_heading:
                story.append(PageBreak())
            if style_name == "Title" or (not story and style_name == "Normal"):
                style = title
            elif style_name == "Heading 1":
                style = h1
            elif style_name == "Heading 2":
                style = h2
            elif style_name == "Heading 3":
                style = h3
            elif intro_index == 1:
                style = subtitle
            elif intro_index == 2:
                style = meta
            else:
                style = body
            story.append(Paragraph(escape(text), style))
            if style_name == "Normal" and intro_index < 3:
                intro_index += 1
        else:
            data = []
            for row_index, row in enumerate(block.rows):
                rendered = []
                for col_index, docx_cell in enumerate(row.cells):
                    style = cell_header if row_index == 0 else cell
                    if len(row.cells) >= 4 and col_index > 0 and row_index > 0:
                        style = cell_center
                    rendered.append(Paragraph(escape(docx_cell.text), style))
                data.append(rendered)
            columns = len(block.columns)
            if columns == 2:
                widths = [1.75 * inch, 5.25 * inch]
            elif columns == 3:
                widths = [1.35 * inch, 2.05 * inch, 3.60 * inch]
            elif columns == 5:
                widths = [2.1 * inch, 1.1 * inch, 1.1 * inch, 1.1 * inch, 1.6 * inch]
            else:
                widths = [7.0 * inch / columns] * columns
            table = LongTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), blue),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9FBAD0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_blue]),
            ]))
            story.extend([table, Spacer(1, 6)])

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D9E2F3"))
        canvas.line(0.72 * inch, 0.50 * inch, 7.78 * inch, 0.50 * inch)
        canvas.setFont("Helvetica", 7.3)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(0.72 * inch, 0.32 * inch, footer_label)
        canvas.drawRightString(7.78 * inch, 0.32 * inch, f"Page {doc.page}")
        canvas.restoreState()

    target = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=0.72 * inch, rightMargin=0.72 * inch, topMargin=0.60 * inch, bottomMargin=0.65 * inch, title=footer_label)
    target.build(story, onFirstPage=footer, onLaterPages=footer)
    print(pdf_path)


for job in JOBS:
    render(*job)
