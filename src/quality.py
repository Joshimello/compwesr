from dataclasses import dataclass


@dataclass(frozen=True)
class QualityPreset:
    jpeg_quality: int
    max_height: int
    video_crf: int


PRESETS: dict[str, QualityPreset] = {
    "high": QualityPreset(jpeg_quality=85, max_height=1080, video_crf=23),
    "medium": QualityPreset(jpeg_quality=70, max_height=720, video_crf=28),
    "low": QualityPreset(jpeg_quality=50, max_height=480, video_crf=32),
}

DEFAULT_PRESET = "medium"
