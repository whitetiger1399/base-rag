"""Generate the expanded Q4 multi-agent data-flow and routing diagram."""

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "shared_output/Q4_Graph_Multi_Agent/Q4_GRAPH_MULTI_AGENT_WORKFLOW.png"
WIDTH, HEIGHT = 1600, 1370


def load_font(size: int, bold: bool = False, mono: bool = False):
    if mono:
        candidates = ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Monaco.ttf"]
    else:
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


TITLE = load_font(40, True)
SUBTITLE = load_font(19)
SECTION = load_font(24, True)
AGENT_TITLE = load_font(22, True)
AGENT_TYPE = load_font(17, True)
BODY = load_font(17)
BODY_BOLD = load_font(17, True)
STATE = load_font(18)
BADGE = load_font(15, True)


def arrow(draw, points, color="#397CB6", width=5, head=14):
    draw.line(points, fill=color, width=width, joint="curve")
    start, end = points[-2], points[-1]
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    left = (end[0] - head * math.cos(angle - math.pi / 6), end[1] - head * math.sin(angle - math.pi / 6))
    right = (end[0] - head * math.cos(angle + math.pi / 6), end[1] - head * math.sin(angle + math.pi / 6))
    draw.polygon((end, left, right), fill=color)


def pill(draw, x, y, value, fill):
    width = draw.textlength(value, font=BADGE) + 22
    draw.rounded_rectangle((x, y, x + width, y + 30), radius=15, fill=fill)
    draw.text((x + 11, y + 6), value, font=BADGE, fill="#FFFFFF")


def line_label(draw, x, y, value, color="#315F86"):
    width = draw.textlength(value, font=BADGE) + 18
    draw.rounded_rectangle((x - 7, y - 4, x + width, y + 27), radius=8, fill="#FFFFFF")
    draw.text((x + 2, y + 3), value, font=BADGE, fill=color)


def agent_card(draw, box, number, title, agent_type, input_lines, output_lines, color, pale):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1 + 7, y1 + 8, x2 + 7, y2 + 8), radius=17, fill="#DCE5EC")
    draw.rounded_rectangle(box, radius=17, fill="#FFFFFF", outline=color, width=3)
    draw.rounded_rectangle((x1, y1, x2, y1 + 48), radius=17, fill=color)
    draw.rectangle((x1, y1 + 30, x2, y1 + 48), fill=color)
    draw.ellipse((x1 + 12, y1 + 10, x1 + 42, y1 + 40), fill="#FFFFFF")
    draw.text((x1 + 27, y1 + 25), number, font=BADGE, fill=color, anchor="mm")
    draw.text((x1 + 52, y1 + 14), title, font=AGENT_TITLE, fill="#FFFFFF")
    draw.rounded_rectangle((x1 + 14, y1 + 58, x2 - 14, y1 + 87), radius=12, fill=pale)
    draw.text((x1 + 26, y1 + 65), agent_type, font=AGENT_TYPE, fill=color)
    draw.text((x1 + 16, y1 + 98), "IN", font=BODY_BOLD, fill=color)
    draw.multiline_text((x1 + 52, y1 + 98), "\n".join(input_lines), font=BODY, fill="#31465A", spacing=3)
    draw.text((x1 + 16, y1 + 137), "OUT", font=BODY_BOLD, fill=color)
    draw.multiline_text((x1 + 62, y1 + 137), "\n".join(output_lines), font=BODY, fill="#31465A", spacing=3)


def state_card(draw, box, heading, lines, color):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1 + 5, y1 + 6, x2 + 5, y2 + 6), radius=14, fill="#DEE7EE")
    draw.rounded_rectangle(box, radius=14, fill="#FFFFFF", outline=color, width=2)
    draw.text((x1 + 14, y1 + 10), heading, font=BODY_BOLD, fill=color)
    draw.multiline_text((x1 + 14, y1 + 36), "\n".join(lines), font=STATE, fill="#273E52", spacing=3)


def terminal(draw, box, title, subtitle, outline, fill, text_fill):
    draw.rounded_rectangle(box, radius=16, fill=fill, outline=outline, width=3)
    x = (box[0] + box[2]) // 2
    draw.text((x, box[1] + 19), title, font=AGENT_TITLE, fill=text_fill, anchor="ma")
    draw.text((x, box[1] + 48), subtitle, font=BODY_BOLD, fill=text_fill, anchor="ma")


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), "#FFFFFF")
    draw = ImageDraw.Draw(image)
    draw.text((42, 24), "Q4  •  Multi-Agent RAG — State, Data & Routing", font=TITLE, fill="#17365D")
    draw.text((45, 76), "Each agent has one job and a declared state contract; the router owns every branch and stopping decision.", font=SUBTITLE, fill="#526777")

    draw.rounded_rectangle((30, 112, 1570, 290), radius=22, fill="#F0F7FC", outline="#397CB6", width=3)
    draw.text((52, 132), "TYPED SHARED STATE", font=SECTION, fill="#276FAE")
    draw.text((335, 138), "Every node reads declared fields, writes its result, and appends a sanitized trace event.", font=BODY, fill="#526777")
    state_boxes = [
        ((50, 175, 335, 278), "QUERY", ["original_query  (fixed)", "active_query  (refinable)"]),
        ((360, 175, 650, 278), "EVIDENCE", ["retrieved_chunks", "safe_chunks", "approved_ids"]),
        ((675, 175, 965, 278), "DECISION", ["verifier_verdict", "missing_facts", "refined_query"]),
        ((990, 175, 1235, 278), "CONTROL", ["retry_count ≤ 2", "filters + max_retries"]),
        ((1260, 175, 1550, 278), "RESULT", ["answer + cited_ids", "abstain_reason + trace"]),
    ]
    for box, heading, lines in state_boxes:
        state_card(draw, box, heading, lines, "#397CB6")

    draw.rounded_rectangle((30, 315, 1570, 1060), radius=22, fill="#F8FBFD", outline="#B7C9D7", width=3)
    draw.text((52, 335), "LOGICAL EXECUTION & DATA FLOW", font=SECTION, fill="#17365D")

    start = (50, 428, 185, 520)
    draw.rounded_rectangle(start, radius=16, fill="#F3F5F7", outline="#66798B", width=3)
    draw.text((117, 448), "START", font=AGENT_TITLE, fill="#31465A", anchor="ma")
    draw.text((117, 482), "question + filters", font=BODY, fill="#526777", anchor="ma")

    retriever = (220, 390, 475, 570)
    safety = (510, 390, 765, 570)
    verifier = (800, 390, 1055, 570)
    answerer = (900, 650, 1170, 830)
    refiner = (500, 650, 770, 830)
    validator = (1280, 650, 1550, 830)
    agent_card(draw, retriever, "1", "RETRIEVER", "SEARCH SPECIALIST", ["active_query + filters"], ["ranked chunks + scores"], "#2878B5", "#EAF4FC")
    agent_card(draw, safety, "2", "SAFETY", "CONTENT POLICY GATE", ["retrieved chunks"], ["safe + quarantined IDs"], "#8A55A0", "#F5ECF8")
    agent_card(draw, verifier, "3", "VERIFIER", "EVIDENCE JUDGE", ["question + safe chunks"], ["verdict + approved IDs"], "#B27612", "#FFF5DF")
    agent_card(draw, answerer, "4", "ANSWERER", "GROUNDED WRITER", ["approved chunks only"], ["cited candidate answer"], "#2D8A62", "#EAF7F1")
    agent_card(draw, refiner, "5", "REFINER", "QUERY PLANNER", ["missing facts"], ["focused active_query"], "#C06E20", "#FFF1E3")
    agent_card(draw, validator, "6", "VALIDATOR", "DETERMINISTIC CHECKER", ["candidate + allow-list"], ["citation result +", "faithfulness score"], "#327A86", "#E9F5F7")

    cx, cy, dw, dh = 1165, 480, 180, 150
    points = [(cx, cy - dh // 2), (cx + dw // 2, cy), (cx, cy + dh // 2), (cx - dw // 2, cy)]
    draw.polygon([(x + 6, y + 7) for x, y in points], fill="#DCE5EC")
    draw.polygon(points, fill="#FFF9E8", outline="#B27612")
    draw.line(points + [points[0]], fill="#B27612", width=4)
    draw.text((cx, cy - 18), "ROUTER", font=AGENT_TITLE, fill="#6D4B0E", anchor="ma")
    draw.text((cx, cy + 17), "conditional edges", font=BODY, fill="#6D4B0E", anchor="ma")

    cited = (990, 930, 1230, 1010)
    abstain = (1290, 930, 1550, 1010)
    terminal(draw, cited, "CITED ANSWER", "→ END", "#2E8B57", "#E9F6EE", "#245B3B")
    terminal(draw, abstain, "SAFE ABSTENTION", "→ END", "#C44C56", "#FDEDEE", "#8C2F38")

    arrow(draw, [(185, 480), (220, 480)])
    arrow(draw, [(475, 480), (510, 480)])
    arrow(draw, [(765, 480), (800, 480)])
    arrow(draw, [(1055, 480), (1075, 480)])
    arrow(draw, [(1165, 555), (1165, 600), (1035, 600), (1035, 650)], color="#2E8B57")
    pill(draw, 1000, 565, "SUFFICIENT → ANSWERER", "#2E8B57")

    arrow(draw, [(1170, 740), (1280, 740)], color="#327A86")
    line_label(draw, 1180, 695, "CANDIDATE", "#327A86")
    arrow(draw, [(1345, 830), (1345, 875), (1200, 875), (1200, 930)], color="#2E8B57")
    pill(draw, 1240, 837, "VALID", "#2E8B57")
    arrow(draw, [(1480, 830), (1480, 930)], color="#C44C56")
    pill(draw, 1492, 862, "INVALID", "#B8424C")

    arrow(draw, [(1100, 535), (850, 605), (635, 650)], color="#C06E20")
    pill(draw, 715, 565, "INSUFFICIENT + NEW FOCUS", "#C06E20")
    arrow(draw, [(500, 740), (345, 740), (345, 570)], color="#C06E20")
    pill(draw, 360, 715, "RETRY COUNT < 2", "#C06E20")

    arrow(draw, [(1255, 480), (1560, 480), (1560, 970), (1550, 970)], color="#C44C56")
    pill(draw, 1360, 445, "FAIL CLOSED", "#B8424C")
    draw.text((1045, 1027), "Unsafe • malformed • unchanged • empty • retries exhausted", font=BODY, fill="#9A313A")

    draw.text((225, 584), "Query-only Chroma snapshot + BM25", font=BODY, fill="#526777")
    draw.text((515, 584), "Quarantined chunks stop here", font=BODY, fill="#7A438E")
    draw.text((805, 365), "Local qwen3:8b structured verdict", font=BODY, fill="#80540C")
    draw.text((905, 625), "Local qwen3:8b • approved evidence only • no tool handle", font=BODY, fill="#256F50")

    draw.rounded_rectangle((30, 1090, 1570, 1340), radius=22, fill="#F5F1FA", outline="#7957B8", width=3)
    draw.text((52, 1112), "SANITIZED OBSERVABILITY BUS", font=SECTION, fill="#68459F")
    draw.text((52, 1162), "EVERY NODE APPENDS", font=BODY_BOLD, fill="#4D3375")
    draw.text((262, 1162), "node • agent type • route • attempt • IDs • duration • verdict • validation result • terminal reason", font=BODY, fill="#55436E")
    draw.text((52, 1204), "Every transition is reviewable without storing raw malicious passages.", font=BODY, fill="#55436E")
    draw.rounded_rectangle((52, 1242, 610, 1305), radius=14, fill="#FFFFFF", outline="#A88DCE", width=2)
    draw.text((70, 1262), "TRACE EXAMPLE", font=BODY_BOLD, fill="#68459F")
    draw.text((220, 1262), "agent=verifier  •  route=refine  •  attempt=1", font=BODY, fill="#55436E")
    arrow(draw, [(1450, 1060), (1450, 1090)], color="#7957B8")
    pill(draw, 1462, 1050, "TRACE", "#6C4CA5")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, quality=95)
    print(OUTPUT)


if __name__ == "__main__":
    main()
