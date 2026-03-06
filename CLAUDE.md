# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync --dev          # install dependencies
uv run pytest          # run all tests
uv run pytest -v       # run tests with output
uv run pytest tests/test_images.py::test_compress_respects_max_height  # run a single test
uv run main.py sample.pptx --quality medium --dry-run  # smoke test
```

`ffmpeg` is bundled via `imageio-ffmpeg` (a project dependency) — no system install required.

## Architecture

The tool is a 4-step pipeline: **read** the `.pptx` (which is a zip), **compress** each media file, **patch** relationship XML if a file is renamed, **write** a new zip as `<stem>_compressed.pptx`.

```
main.py          CLI (argparse) → calls compress_pptx(), prints report
src/
  compress.py    Core orchestration: opens input zip, iterates entries,
                 routes media to images.py or videos.py, writes output zip.
                 Also contains _patch_rels_for_rename() and _queue_rels_rename()
                 for updating ppt/slides/_rels/*.rels when a container changes
                 (e.g. .avi → .mp4).
  images.py      compress_image() — Pillow JPEG recompression + resize.
                 RGBA/palette modes are composited onto white before JPEG save.
  videos.py      compress_video() — ffmpeg subprocess via imageio_ffmpeg. Always outputs .mp4.
  quality.py     QualityPreset dataclass + PRESETS dict (high/medium/low).
  report.py      ItemResult, Report, print_summary(). Tracks per-item and
                 aggregate size before/after.
tests/
  conftest.py    Fixtures: synthetic .pptx built with zipfile + Pillow in memory.
```

### Key behaviours
- Both `compress_image` and `compress_video` return the **original bytes unchanged** (skipping) if savings are < 5%, or if ffmpeg fails.
- `pythonpath = ["src", "."]` in `pyproject.toml` makes `src/` modules and root `main.py` importable during tests without installation.
