import io

from PIL import Image

from quality import QualityPreset

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
MIN_SAVINGS_RATIO = 0.05


def compress_image(data: bytes, preset: QualityPreset, original_name: str) -> tuple[bytes, str]:
    """Compress image data to JPEG. Returns (compressed_bytes, new_filename)."""
    img = Image.open(io.BytesIO(data))

    # Resize if taller than max_height
    w, h = img.size
    max_h = preset.max_height
    if h > max_h:
        scale = max_h / h
        img = img.resize((int(w * scale), max_h), Image.LANCZOS)

    # Composite RGBA/palette onto white background before JPEG conversion
    if img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=preset.jpeg_quality, optimize=True)
    compressed = buf.getvalue()

    # Skip if savings < 5%
    if len(data) > 0 and (len(data) - len(compressed)) / len(data) < MIN_SAVINGS_RATIO:
        return data, original_name

    # Always output .jpg
    stem = original_name.rsplit(".", 1)[0]
    new_name = stem + ".jpg"
    return compressed, new_name
