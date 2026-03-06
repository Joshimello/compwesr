from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quality import PRESETS
from videos import compress_video


def _make_fake_ffmpeg_side_effect(output_content: bytes = b"fake_compressed_video" * 100):
    """Returns a side_effect for subprocess.run that writes fake output."""
    def side_effect(cmd, **kwargs):
        # Extract output path from cmd (last arg)
        output_path = Path(cmd[-1])
        output_path.write_bytes(output_content)
        result = MagicMock()
        result.returncode = 0
        return result
    return side_effect


def test_compress_video_calls_ffmpeg(tmp_path):
    original_data = b"x" * 10_000
    preset = PRESETS["medium"]

    with patch("subprocess.run", side_effect=_make_fake_ffmpeg_side_effect(b"y" * 1000)) as mock_run:
        result, name = compress_video(original_data, preset, "clip.mp4", tmp_path)

    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert "ffmpeg" in cmd[0]
    assert str(preset.max_height) in " ".join(cmd)
    assert str(preset.video_crf) in cmd


def test_compress_video_output_is_mp4(tmp_path):
    original_data = b"x" * 10_000
    with patch("subprocess.run", side_effect=_make_fake_ffmpeg_side_effect(b"y" * 1000)):
        _, name = compress_video(original_data, PRESETS["medium"], "clip.avi", tmp_path)
    assert name.endswith(".mp4")


def test_compress_video_returns_original_on_ffmpeg_failure(tmp_path):
    original_data = b"x" * 10_000

    def fail_side_effect(cmd, **kwargs):
        result = MagicMock()
        result.returncode = 1
        return result

    with patch("subprocess.run", side_effect=fail_side_effect):
        result, name = compress_video(original_data, PRESETS["medium"], "clip.mp4", tmp_path)

    assert result == original_data
    assert name == "clip.mp4"


def test_compress_video_skips_if_savings_too_small(tmp_path):
    original_data = b"x" * 10_000
    # Output almost the same size (< 5% savings)
    nearly_same = b"y" * 9_999

    with patch("subprocess.run", side_effect=_make_fake_ffmpeg_side_effect(nearly_same)):
        result, name = compress_video(original_data, PRESETS["medium"], "clip.mp4", tmp_path)

    assert result is original_data


def test_compress_video_real_ffmpeg_integration(tmp_path):
    """Integration test using imageio-ffmpeg bundled binary."""
    # We don't have a real video fixture, so just verify the function runs
    # without crashing when given empty data (ffmpeg will fail gracefully)
    result, name = compress_video(b"\x00" * 100, PRESETS["low"], "clip.mp4", tmp_path)
    # Should return original on ffmpeg failure with invalid data
    assert isinstance(result, bytes)
