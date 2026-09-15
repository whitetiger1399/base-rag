"""Build the Q3 guardrails, evaluation, and agent workflow diagram."""

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "shared_output/Q3_Guardrails_Eval_Agents/Q3_GUARDRAIL_EVAL_AGENT_WORKFLOW.png"
WIDTH, HEIGHT = 1800, 720


def font(size: int, bold: bool = False):
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


TITLE = font(36, bold=True)
LANE = font(23, bold=True)
BOX = font(19, bold=True)
SMALL = font(16)
LABEL = font(15, bold=True)


def centered_text(draw, box, lines, text_font, fill="#17365D", spacing=5):
    text = "\n".join(lines)
    bounds = draw.multiline_textbbox((0, 0), text, font=text_font, spacing=spacing, align="center")
    text_width = bounds[2] - bounds[0]
    text_height = bounds[3] - bounds[1]
    x = box[0] + (box[2] - box[0] - text_width) / 2
    y = box[1] + (box[3] - box[1] - text_height) / 2 - bounds[1]
    draw.multiline_text((x, y), text, font=text_font, fill=fill, spacing=spacing, align="center")


def node(draw, box, lines, fill="#EAF2F8", outline="#1F4E78", text_fill="#17365D"):
    draw.rounded_rectangle(box, radius=16, fill=fill, outline=outline, width=3)
    centered_text(draw, box, lines, BOX, text_fill)


def arrow(draw, start, end, color="#46627A", width=5, head=14):
    draw.line([start, end], fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    left = (
        end[0] - head * math.cos(angle - math.pi / 6),
        end[1] - head * math.sin(angle - math.pi / 6),
    )
    right = (
        end[0] - head * math.cos(angle + math.pi / 6),
        end[1] - head * math.sin(angle + math.pi / 6),
    )
    draw.polygon([end, left, right], fill=color)


def label(draw, xy, text, fill="#46627A"):
    draw.rounded_rectangle((xy[0] - 7, xy[1] - 4, xy[0] + draw.textlength(text, font=LABEL) + 8, xy[1] + 22), radius=6, fill="white")
    draw.text(xy, text, font=LABEL, fill=fill)


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)

    draw.text((55, 28), "Q3 Guardrails, Evaluation & Agent Workflow", font=TITLE, fill="#17365D")
    draw.text((58, 78), "Live decisions remain bounded; sanitized traces feed repeatable quality and safety evaluation.", font=SMALL, fill="#526777")

    # Live guarded RAG lane.
    draw.rounded_rectangle((35, 118, 1765, 410), radius=24, fill="#F7FAFC", outline="#B8CAD8", width=3)
    draw.text((62, 136), "LIVE GUARDED RAG PATH", font=LANE, fill="#1F4E78")

    boxes = [
        (60, 202, 245, 300),
        (295, 202, 500, 300),
        (550, 202, 790, 300),
        (840, 202, 1080, 300),
        (1130, 202, 1315, 300),
        (1365, 202, 1585, 300),
    ]
    texts = [
        ["User", "query"],
        ["Query safety", "screen"],
        ["Read-only hybrid", "retriever"],
        ["Chunk safety +", "quarantine"],
        ["Verifier", "agent"],
        ["Answerer + citation", "validation"],
    ]
    for box, lines in zip(boxes, texts):
        node(draw, box, lines)
    for left, right in zip(boxes[:-1], boxes[1:]):
        arrow(draw, (left[2], 251), (right[0], 251))

    success = (1618, 184, 1738, 252)
    abstain = (1618, 310, 1738, 378)
    node(draw, success, ["Cited", "answer"], fill="#E7F5EC", outline="#2E7D4F", text_fill="#245B3B")
    node(draw, abstain, ["Safe", "abstention"], fill="#FDEBEC", outline="#B64343", text_fill="#8C2F2F")
    arrow(draw, (1585, 235), (1618, 218), color="#2E7D4F")
    label(draw, (1574, 190), "valid")
    arrow(draw, (1585, 278), (1618, 344), color="#B64343")
    label(draw, (1569, 302), "unsafe / failed")

    # Bounded retry loop from verifier back to retrieval.
    retry_y = 350
    draw.line([(1222, 300), (1222, retry_y), (670, retry_y), (670, 300)], fill="#C17C16", width=5)
    arrow(draw, (670, retry_y), (670, 300), color="#C17C16")
    label(draw, (850, 332), "insufficient → refine query → retry ≤ 2")

    # Evaluation and observability lane.
    draw.rounded_rectangle((35, 438, 1765, 685), radius=24, fill="#FBFAF5", outline="#D8C9A8", width=3)
    draw.text((62, 456), "EVALUATION & OBSERVABILITY", font=LANE, fill="#785516")
    eval_boxes = [
        (60, 525, 330, 625),
        (385, 525, 650, 625),
        (705, 525, 1020, 625),
        (1075, 525, 1350, 625),
        (1405, 525, 1728, 625),
    ]
    eval_texts = [
        ["Golden set +", "sanitized traces"],
        ["Retrieval metrics", "Recall@k • MRR"],
        ["Ragas evidence quality", "6 separate metrics"],
        ["Safety + abstention", "precision • recall • F1"],
        ["MLflow run + report", "versions • latency • failures"],
    ]
    for box, lines in zip(eval_boxes, eval_texts):
        node(draw, box, lines, fill="#FFF8E7", outline="#A87820", text_fill="#65470F")
    for left, right in zip(eval_boxes[:-1], eval_boxes[1:]):
        arrow(draw, (left[2], 575), (right[0], 575), color="#A87820")

    # Sanitized live trace feeds evaluation without exposing raw malicious text.
    arrow(draw, (1450, 410), (1450, 525), color="#6A5D91")
    label(draw, (1464, 456), "sanitized audit events", fill="#6A5D91")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, quality=95)
    print(OUTPUT)


if __name__ == "__main__":
    main()
