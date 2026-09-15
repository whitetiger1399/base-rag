"""Build the Q1 retrieval workflow diagram used by DOCX and PDF outputs."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path("shared_output/Q1_Retrieval_Design/Q1_RETRIEVAL_WORKFLOW.png")
WIDTH, HEIGHT = 1800, 560
NAVY = "#17365D"
BLUE = "#1F4E78"
PALE = "#EAF2F8"
GREEN = "#E8F5E9"
AMBER = "#FFF4D6"
RED = "#FDECEC"
GREY = "#52606D"


def font(size: int, bold: bool = False):
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
             "/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    return ImageFont.truetype(str(next(path for path in candidates if path.exists())), size)


canvas = Image.new("RGB", (WIDTH, HEIGHT), "white")
draw = ImageDraw.Draw(canvas)
title_font = font(34, True)
lane_font = font(24, True)
box_font = font(22, True)
small_font = font(18)


def centered(text, box, chosen_font, fill=NAVY):
    lines = text.split("\n")
    heights = [draw.textbbox((0, 0), line, font=chosen_font)[3] for line in lines]
    total = sum(heights) + 5 * (len(lines) - 1)
    y = box[1] + (box[3] - box[1] - total) / 2
    for line, height in zip(lines, heights):
        bounds = draw.textbbox((0, 0), line, font=chosen_font)
        x = box[0] + (box[2] - box[0] - (bounds[2] - bounds[0])) / 2
        draw.text((x, y), line, font=chosen_font, fill=fill)
        y += height + 5


def node(x, y, w, h, text, fill=PALE, outline=BLUE):
    box = (x, y, x + w, y + h)
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=outline, width=4)
    centered(text, box, box_font)
    return box


def arrow(start, end, fill=GREY):
    draw.line((start, end), fill=fill, width=5)
    x, y = end
    draw.polygon([(x, y), (x - 15, y - 9), (x - 15, y + 9)], fill=fill)


draw.text((60, 22), "Q1 Retrieval Workflow", font=title_font, fill=NAVY)
draw.text((60, 72), "OFFLINE INDEX BUILD", font=lane_font, fill=BLUE)

top_y, top_w, top_h = 108, 330, 92
top_nodes = [
    node(60, top_y, top_w, top_h, "Workbook rows\n+ paragraph IDs"),
    node(485, top_y, top_w, top_h, "Detect headings\n+ normalize text"),
    node(910, top_y, top_w, top_h, "Paragraph-aware chunks\n+ metadata"),
    node(1335, top_y, 400, top_h, "MiniLM / Chroma\n+ BM25 index", GREEN),
]
for left, right in zip(top_nodes, top_nodes[1:]):
    arrow((left[2] + 12, (left[1] + left[3]) / 2),
          (right[0] - 12, (right[1] + right[3]) / 2))

draw.text((60, 238), "ONLINE QUERY AND EVIDENCE SELECTION", font=lane_font, fill=BLUE)
bottom_y, bottom_w, bottom_h, gap = 278, 230, 88, 22
labels = [
    "User\nquestion", "Validate\nfilters", "Vector + BM25\nsearch",
    "RRF\nfusion", "Evidence\ngate", "Top-k cited\nevidence",
]
bottom_nodes = []
for index, label in enumerate(labels):
    fill = GREEN if index == 5 else PALE
    bottom_nodes.append(node(60 + index * (bottom_w + gap), bottom_y,
                             bottom_w, bottom_h, label, fill))
for left, right in zip(bottom_nodes, bottom_nodes[1:]):
    arrow((left[2] + 5, (left[1] + left[3]) / 2),
          (right[0] - 5, (right[1] + right[3]) / 2))

# The persistent index feeds both retrieval branches, while insufficient
# evidence exits without generation.
draw.line((1535, 202, 1535, 230, 690, 230, 690, bottom_y - 10), fill=GREY, width=4)
draw.polygon([(690, bottom_y), (681, bottom_y - 15), (699, bottom_y - 15)], fill=GREY)

gate = bottom_nodes[4]
abstain = node(gate[0], 430, bottom_w, 70, "Cannot find\nin sources", RED, "#B42318")
draw.line(((gate[0] + gate[2]) / 2, gate[3], (gate[0] + gate[2]) / 2, abstain[1] - 10),
          fill="#B42318", width=4)
draw.polygon([((gate[0] + gate[2]) / 2, abstain[1]),
              ((gate[0] + gate[2]) / 2 - 9, abstain[1] - 15),
              ((gate[0] + gate[2]) / 2 + 9, abstain[1] - 15)], fill="#B42318")
draw.text(((gate[0] + gate[2]) / 2 + 14, 390), "insufficient",
          font=small_font, fill="#B42318")
draw.text((gate[2] + 18, bottom_y - 28), "sufficient",
          font=small_font, fill="#217A3C")

OUT.parent.mkdir(parents=True, exist_ok=True)
canvas.save(OUT, optimize=True)
print(OUT)
