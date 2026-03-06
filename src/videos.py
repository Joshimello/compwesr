import subprocess
from pathlib import Path

import imageio_ffmpeg

from quality import QualityPreset

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".wmv", ".mkv", ".m4v"}
MIN_SAVINGS_RATIO = 0.05


def compress_video(
    data: bytes,
    preset: QualityPreset,
    original_name: str,
    tmp_dir: Path,
) -> tuple[bytes, str]:
    """Compress video data via ffmpeg. Returns (compressed_bytes, new_filename)."""
    stem = original_name.rsplit(".", 1)[0]
    suffix = "." + original_name.rsplit(".", 1)[-1] if "." in original_name else ".mp4"

    input_path = tmp_dir / original_name
    output_name = stem + ".mp4"
    output_path = tmp_dir / output_name

    input_path.write_bytes(data)

    cmd = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-y",
        "-i", str(input_path),
        "-vf", f"scale=-2:{preset.max_height}",
        "-crf", str(preset.video_crf),
        "-preset", "fast",
        "-movflags", "+faststart",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        # Return original on failure
        return data, original_name

    compressed = output_path.read_bytes()

    # Skip if savings < 5%
    if len(data) > 0 and (len(data) - len(compressed)) / len(data) < MIN_SAVINGS_RATIO:
        return data, original_name

    return compressed, output_name
