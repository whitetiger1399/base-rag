from pathlib import Path

from openpyxl import Workbook

from src.chunking import chunk_booklet, is_heading, normalize_text, split_long_text


def test_heading_detection() -> None:
    assert is_heading("1.2.1 Community-based surveillance")
    assert is_heading("SECTION 4: INVESTIGATE OUTBREAKS")
    assert not is_heading("This is an ordinary explanatory sentence.")


def test_normalize_text_removes_artifacts() -> None:
    assert normalize_text("Malawi\ufdd0  public\n health") == "Malawi public health"


def test_split_long_text_respects_limit() -> None:
    text = "First sentence has useful evidence. " * 100
    parts = split_long_text(text, max_chars=200)
    assert len(parts) > 1
    assert max(map(len, parts)) <= 200


def test_chunk_booklet_preserves_metadata(tmp_path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append([1, "1.1 Surveillance"])
    sheet.append([2, "First explanatory paragraph."])
    sheet.append([3, "Second explanatory paragraph."])
    path = tmp_path / "TG Booklet Test.xlsx"
    workbook.save(path)

    chunks = chunk_booklet(path, target_chars=500, max_chars=800)

    assert len(chunks) == 1
    assert chunks[0].doc_id == "TG_Booklet_Test"
    assert chunks[0].section == "1.1 Surveillance"
    assert chunks[0].paragraph_start == 1
    assert chunks[0].paragraph_end == 3
    assert chunks[0].chunk_id.startswith("TG_Booklet_Test:p1-p3")
