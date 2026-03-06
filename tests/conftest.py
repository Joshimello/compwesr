"""Shared fixtures for compwesr tests."""
import io
import zipfile

import pytest
from PIL import Image


def _make_jpeg_bytes(width: int = 200, height: int = 200) -> bytes:
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def _make_png_bytes(width: int = 200, height: int = 200) -> bytes:
    img = Image.new("RGBA", (width, height), color=(100, 150, 200, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_pptx_bytes(include_image: bool = True, include_video: bool = False) -> bytes:
    """Build a minimal .pptx zip in memory."""
    buf = io.BytesIO()

    slide_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree/></p:cSld>
</p:sld>"""

    rels_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">"""

    if include_image:
        rels_xml += b"""
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
    Target="../media/image1.jpg"/>"""

    if include_video:
        rels_xml += b"""
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/video"
    Target="../media/video1.mp4"/>"""

    rels_xml += b"\n</Relationships>"

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", b'<?xml version="1.0"?><Types/>')
        zf.writestr("ppt/slides/slide1.xml", slide_xml)
        zf.writestr("ppt/slides/_rels/slide1.xml.rels", rels_xml)

        if include_image:
            zf.writestr("ppt/media/image1.jpg", _make_jpeg_bytes(800, 600))

        if include_video:
            # Minimal fake MP4-ish data (not real video, tests mock ffmpeg)
            zf.writestr("ppt/media/video1.mp4", b"\x00" * 1024)

    return buf.getvalue()


@pytest.fixture
def sample_pptx_bytes():
    return _make_pptx_bytes(include_image=True, include_video=False)


@pytest.fixture
def sample_pptx_path(tmp_path, sample_pptx_bytes):
    p = tmp_path / "sample.pptx"
    p.write_bytes(sample_pptx_bytes)
    return p


@pytest.fixture
def jpeg_bytes():
    return _make_jpeg_bytes()


@pytest.fixture
def png_bytes():
    return _make_png_bytes()
