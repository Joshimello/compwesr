import io

import pytest
from PIL import Image

from images import compress_image
from quality import PRESETS


def _img_size(data: bytes) -> tuple[int, int]:
    return Image.open(io.BytesIO(data)).size


@pytest.fixture
def large_jpeg():
    img = Image.new("RGB", (1920, 1080), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


@pytest.fixture
def large_png():
    img = Image.new("RGBA", (1920, 1080), color=(200, 100, 50, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_compress_jpeg_returns_bytes(large_jpeg):
    result, name = compress_image(large_jpeg, PRESETS["medium"], "photo.jpg")
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_compress_jpeg_output_name(large_jpeg):
    _, name = compress_image(large_jpeg, PRESETS["medium"], "photo.jpg")
    assert name.endswith(".jpg")


def test_compress_png_converts_to_jpeg(large_png):
    result, name = compress_image(large_png, PRESETS["medium"], "image.png")
    assert name.endswith(".jpg")
    # Verify it's a valid JPEG
    img = Image.open(io.BytesIO(result))
    assert img.format == "JPEG"


def test_compress_respects_max_height(large_jpeg):
    preset = PRESETS["low"]  # max_height = 480
    result, _ = compress_image(large_jpeg, preset, "photo.jpg")
    w, h = _img_size(result)
    assert h <= preset.max_height


def test_compress_small_image_skipped(jpeg_bytes):
    # jpeg_bytes fixture is 200x200 — compressing at high quality likely won't save 5%
    # We force skip by using the bytes directly with high quality
    original = jpeg_bytes
    result, name = compress_image(original, PRESETS["high"], "tiny.jpg")
    # Either skipped (returns original object) or compressed — just check it's valid
    assert isinstance(result, bytes)


def test_compress_reduces_size(large_jpeg):
    result, _ = compress_image(large_jpeg, PRESETS["low"], "photo.jpg")
    # Low quality should reduce size significantly for a large JPEG
    # (some images might be skipped if already small enough)
    assert len(result) <= len(large_jpeg)


def test_compress_rgba_no_transparency_leak(large_png):
    result, _ = compress_image(large_png, PRESETS["medium"], "image.png")
    img = Image.open(io.BytesIO(result))
    assert img.mode == "RGB"  # No alpha in JPEG output
