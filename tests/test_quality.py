import pytest

from quality import DEFAULT_PRESET, PRESETS, QualityPreset


def test_all_presets_exist():
    assert set(PRESETS) == {"high", "medium", "low"}


def test_preset_types():
    for preset in PRESETS.values():
        assert isinstance(preset, QualityPreset)


def test_high_preset():
    p = PRESETS["high"]
    assert p.jpeg_quality == 85
    assert p.max_height == 1080
    assert p.video_crf == 23


def test_medium_preset():
    p = PRESETS["medium"]
    assert p.jpeg_quality == 70
    assert p.max_height == 720
    assert p.video_crf == 28


def test_low_preset():
    p = PRESETS["low"]
    assert p.jpeg_quality == 50
    assert p.max_height == 480
    assert p.video_crf == 32


def test_default_preset():
    assert DEFAULT_PRESET == "medium"
    assert DEFAULT_PRESET in PRESETS


def test_presets_are_frozen():
    with pytest.raises(Exception):
        PRESETS["high"].jpeg_quality = 99  # type: ignore[misc]


def test_quality_ordering():
    # Higher quality = higher JPEG quality, lower CRF
    assert PRESETS["high"].jpeg_quality > PRESETS["medium"].jpeg_quality > PRESETS["low"].jpeg_quality
    assert PRESETS["high"].video_crf < PRESETS["medium"].video_crf < PRESETS["low"].video_crf
    assert PRESETS["high"].max_height > PRESETS["medium"].max_height > PRESETS["low"].max_height
