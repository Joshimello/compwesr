import io
import zipfile

import pytest

from compress import _patch_rels_for_rename, compress_pptx
from quality import PRESETS


def test_patch_rels_for_rename():
    xml = b'<Relationship Target="../media/image1.png"/>'
    patched = _patch_rels_for_rename(xml, "image1.png", "image1.jpg")
    assert b'Target="../media/image1.jpg"' in patched
    assert b'Target="../media/image1.png"' not in patched


def test_patch_rels_no_change_when_not_found():
    xml = b'<Relationship Target="../media/other.png"/>'
    patched = _patch_rels_for_rename(xml, "image1.png", "image1.jpg")
    assert patched == xml


def test_compress_pptx_creates_output(sample_pptx_path, tmp_path):
    report = compress_pptx(sample_pptx_path, PRESETS["medium"])
    output = sample_pptx_path.with_name("sample_compressed.pptx")
    assert output.exists()


def test_compress_pptx_output_is_valid_zip(sample_pptx_path):
    compress_pptx(sample_pptx_path, PRESETS["medium"])
    output = sample_pptx_path.with_name("sample_compressed.pptx")
    assert zipfile.is_zipfile(output)


def test_compress_pptx_dry_run_no_output(sample_pptx_path):
    compress_pptx(sample_pptx_path, PRESETS["medium"], dry_run=True)
    output = sample_pptx_path.with_name("sample_compressed.pptx")
    assert not output.exists()


def test_compress_pptx_backup_created(sample_pptx_path):
    compress_pptx(sample_pptx_path, PRESETS["medium"], backup=True)
    backup = sample_pptx_path.with_name("sample_backup.pptx")
    assert backup.exists()


def test_compress_pptx_output_smaller_or_equal(sample_pptx_path):
    compress_pptx(sample_pptx_path, PRESETS["low"])
    output = sample_pptx_path.with_name("sample_compressed.pptx")
    assert output.stat().st_size <= sample_pptx_path.stat().st_size * 1.05  # allow 5% margin for zip overhead


def test_compress_pptx_report_has_image_item(sample_pptx_path):
    report = compress_pptx(sample_pptx_path, PRESETS["medium"])
    # sample has one image
    image_items = [i for i in report.items if i.kind == "image"]
    assert len(image_items) == 1


def test_compress_pptx_images_only_skips_videos(tmp_path):
    """images_only flag should skip video processing."""
    # Build pptx with both image and video marker
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", b'<?xml version="1.0"?><Types/>')
        zf.writestr("ppt/slides/slide1.xml", b"<slide/>")
        zf.writestr("ppt/slides/_rels/slide1.xml.rels", b"<Relationships/>")
        import io as _io
        from PIL import Image as _Image
        img = _Image.new("RGB", (800, 600), color=(100, 150, 200))
        buf2 = _io.BytesIO()
        img.save(buf2, format="JPEG", quality=95)
        zf.writestr("ppt/media/image1.jpg", buf2.getvalue())
        zf.writestr("ppt/media/video1.mp4", b"\x00" * 512)
    p = tmp_path / "deck.pptx"
    p.write_bytes(buf.getvalue())

    report = compress_pptx(p, PRESETS["medium"], images_only=True)
    video_items = [i for i in report.items if i.kind == "video"]
    assert len(video_items) == 0


def test_compress_pptx_preserves_non_media_entries(sample_pptx_path):
    compress_pptx(sample_pptx_path, PRESETS["medium"])
    output = sample_pptx_path.with_name("sample_compressed.pptx")
    with zipfile.ZipFile(output) as zout:
        names = zout.namelist()
    assert "[Content_Types].xml" in names
    assert "ppt/slides/slide1.xml" in names
