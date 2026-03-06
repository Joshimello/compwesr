import io

import pytest

from report import ItemResult, Report, _fmt, print_summary


def test_fmt_bytes():
    assert _fmt(500) == "500 B"


def test_fmt_kb():
    assert _fmt(1500) == "1.5 KB"


def test_fmt_mb():
    assert _fmt(2_500_000) == "2.5 MB"


def test_item_result_saved():
    item = ItemResult("img.jpg", "image", original_size=1000, compressed_size=600)
    assert item.saved == 400


def test_report_add_updates_totals():
    report = Report("in.pptx", "out.pptx")
    report.add(ItemResult("a.jpg", "image", 1000, 600))
    report.add(ItemResult("b.jpg", "image", 2000, 800))
    assert report.original_total == 3000
    assert report.compressed_total == 1400


def test_report_images_videos_filter():
    report = Report("in.pptx", "out.pptx")
    report.add(ItemResult("a.jpg", "image", 1000, 600))
    report.add(ItemResult("b.mp4", "video", 5000, 2000))
    assert len(report.images) == 1
    assert len(report.videos) == 1


def test_report_skipped_excluded_from_summary():
    report = Report("in.pptx", "out.pptx")
    report.add(ItemResult("a.jpg", "image", 1000, 1000, skipped=True))
    assert len(report.images) == 0


def test_reduction_pct_zero_when_no_items():
    report = Report("in.pptx", "out.pptx")
    assert report.reduction_pct == 0.0


def test_reduction_pct():
    report = Report("in.pptx", "out.pptx")
    report.add(ItemResult("a.jpg", "image", 100, 25))
    assert report.reduction_pct == pytest.approx(75.0)


def test_print_summary_dry_run(capsys):
    report = Report("deck.pptx", "deck_compressed.pptx")
    report.add(ItemResult("img.jpg", "image", 1_000_000, 300_000))
    print_summary(report, dry_run=True)
    out = capsys.readouterr().out
    assert "Dry run" in out
    assert "Compressing deck.pptx" in out


def test_print_summary_normal(capsys):
    report = Report("deck.pptx", "deck_compressed.pptx")
    report.add(ItemResult("img.jpg", "image", 1_000_000, 300_000))
    print_summary(report, dry_run=False)
    out = capsys.readouterr().out
    assert "Saved:" in out
    assert "deck_compressed.pptx" in out
