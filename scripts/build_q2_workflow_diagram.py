"""Generate the expanded Q2 end-to-end RAG workflow diagram."""

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "shared_output/Q2_RAG_Demo/docs/Q2_RAG_WORKFLOW.png"
WIDTH, HEIGHT = 1800, 950


def load_font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE = load_font(42, True)
SUBTITLE = load_font(19)
LANE = load_font(23, True)
BOX = load_font(20, True)
DETAIL = load_font(15)
BADGE = load_font(14, True)


def text_center(draw, box, lines, font=BOX, fill="#17365D", spacing=4):
    value = "\n".join(lines)
    bounds = draw.multiline_textbbox((0, 0), value, font=font, spacing=spacing, align="center")
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    x = box[0] + (box[2] - box[0] - width) / 2
    y = box[1] + (box[3] - box[1] - height) / 2 - bounds[1]
    draw.multiline_text((x, y), value, font=font, fill=fill, spacing=spacing, align="center")


def card(draw, box, lines, fill, outline, text_fill="#17365D", radius=16, shadow=True):
    if shadow:
        shadow_box = (box[0] + 7, box[1] + 8, box[2] + 7, box[3] + 8)
        draw.rounded_rectangle(shadow_box, radius=radius, fill="#DCE5EC")
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=3)
    text_center(draw, box, lines, fill=text_fill)


def arrow(draw, start, end, color="#7FC8FF", width=5, head=14):
    draw.line((start, end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    left = (end[0] - head * math.cos(angle - math.pi / 6), end[1] - head * math.sin(angle - math.pi / 6))
    right = (end[0] - head * math.cos(angle + math.pi / 6), end[1] - head * math.sin(angle + math.pi / 6))
    draw.polygon((end, left, right), fill=color)


def badge(draw, x, y, value, fill, outline):
    width = draw.textlength(value, font=BADGE) + 22
    draw.rounded_rectangle((x, y, x + width, y + 29), radius=14, fill=fill, outline=outline, width=2)
    draw.text((x + 11, y + 6), value, font=BADGE, fill="#FFFFFF")


def lane(draw, box, title, accent, fill):
    draw.rounded_rectangle(box, radius=24, fill=fill, outline=accent, width=3)
    draw.text((box[0] + 25, box[1] + 18), title, font=LANE, fill=accent)


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), "#FFFFFF")
    draw = ImageDraw.Draw(image)
    draw.text((48, 25), "Q2  •  Malawi Local RAG — End-to-End Workflow", font=TITLE, fill="#17365D")
    draw.text((52, 80), "Six workbooks become traceable evidence; every answer stays local, cited, observable, and safely bounded.", font=SUBTITLE, fill="#526777")

    lane(draw, (35, 120, 1765, 332), "01  KNOWLEDGE BUILD  •  offline / explicit maintenance", "#168F83", "#F0FAF8")
    build_boxes = [(70, 194, 325, 286), (400, 194, 680, 286), (755, 194, 1025, 286), (1100, 194, 1390, 286), (1465, 183, 1725, 297)]
    build_labels = [["6 Excel workbooks", "source rows"], ["Section-aware chunking", "merge + provenance"], ["1,036 JSONL chunks", "stable IDs + metadata"], ["MiniLM vectors", "+ BM25 lexical index"], ["Canonical stores", "locked read-only"]]
    for box, lines in zip(build_boxes, build_labels):
        card(draw, box, lines, "#FFFFFF", "#2AA69A")
    for left, right in zip(build_boxes[:-1], build_boxes[1:]):
        arrow(draw, (left[2] + 7, (left[1] + left[3]) // 2), (right[0] - 8, (right[1] + right[3]) // 2), "#2AA69A")
    badge(draw, 1547, 257, "IMMUTABLE", "#168F83", "#2AA69A")

    lane(draw, (35, 352, 1765, 682), "02  LIVE ANSWER PATH  •  Streamlit / CLI / batch", "#276FAE", "#F1F7FC")
    live_boxes = [(62, 438, 247, 548), (285, 438, 480, 548), (520, 412, 850, 576), (890, 438, 1085, 548), (1125, 438, 1315, 548), (1355, 438, 1545, 548)]
    live_labels = [["Question", "+ top_k"], ["Validate +", "query safety"], [""], ["Evidence gate", "+ quarantine"], ["Local Ollama", "qwen3:8b"], ["Citation +", "answer validation"]]
    for box, lines in zip(live_boxes, live_labels):
        card(draw, box, lines, "#FFFFFF", "#3C83C3")
    for left, right in zip(live_boxes[:-1], live_boxes[1:]):
        arrow(draw, (left[2] + 7, 493), (right[0] - 8, 493), "#3C83C3")
    draw.text((685, 438), "HYBRID RETRIEVER", font=BOX, fill="#17365D", anchor="mm")
    draw.rounded_rectangle((545, 470, 682, 548), radius=11, fill="#EAF4FC", outline="#639ED0", width=2)
    draw.rounded_rectangle((694, 470, 825, 548), radius=11, fill="#EAF4FC", outline="#639ED0", width=2)
    text_center(draw, (545, 470, 682, 548), ["Chroma", "semantic"], DETAIL, fill="#17365D")
    text_center(draw, (694, 470, 825, 548), ["BM25", "exact terms"], DETAIL, fill="#17365D")
    draw.text((685, 558), "RRF fusion + metadata filters", font=DETAIL, fill="#315F86", anchor="mm")

    cited, abstain = (1590, 407, 1728, 476), (1590, 526, 1728, 595)
    card(draw, cited, ["Cited", "answer"], "#E7F5EC", "#2E8B57", text_fill="#245B3B", shadow=False)
    card(draw, abstain, ["Safe", "abstention"], "#FDEBEC", "#C44C56", text_fill="#8C2F38", shadow=False)
    arrow(draw, (1545, 472), (1590, 442), "#2E8B57")
    arrow(draw, (1545, 515), (1590, 560), "#C44C56")
    badge(draw, 1572, 382, "VALID", "#2E8B57", "#2E8B57")
    badge(draw, 1548, 600, "WEAK / UNSAFE", "#B8424C", "#B8424C")

    draw.line((1595, 297, 1595, 337, 685, 337, 685, 412), fill="#7957B8", width=5)
    arrow(draw, (685, 337), (685, 412), "#7957B8")
    badge(draw, 940, 323, "PRIVATE SNAPSHOT  •  QUERY-ONLY ADAPTER", "#6C4CA5", "#6C4CA5")
    draw.text((78, 615), "UNTRUSTED DATA", font=BADGE, fill="#A7333E")
    draw.text((235, 615), "→ structured source blocks → no raw SQL → allow-listed filters → exact chunk citations", font=DETAIL, fill="#526777")

    lane(draw, (35, 705, 1765, 918), "03  EVALUATION & OBSERVABILITY  •  evidence before confidence", "#A66B08", "#FFF8E8")
    eval_boxes = [(68, 783, 350, 872), (420, 783, 700, 872), (770, 783, 1060, 872), (1130, 783, 1410, 872), (1480, 783, 1728, 872)]
    eval_labels = [["Golden set +", "sanitized live traces"], ["Recall@k • MRR", "citations • abstention"], ["Ragas quality", "6 separate metrics"], ["MLflow + reports", "versions • latency • failures"], ["Tune settings", "then rebuild / rerun"]]
    for box, lines in zip(eval_boxes, eval_labels):
        card(draw, box, lines, "#FFFFFF", "#C58A26", text_fill="#65470F")
    for left, right in zip(eval_boxes[:-1], eval_boxes[1:]):
        arrow(draw, (left[2] + 7, 828), (right[0] - 8, 828), "#C58A26")
    arrow(draw, (1450, 682), (1450, 783), "#7957B8")
    badge(draw, 1465, 710, "SANITIZED TRACE", "#6C4CA5", "#6C4CA5")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, quality=95)
    print(OUTPUT)


if __name__ == "__main__":
    main()
