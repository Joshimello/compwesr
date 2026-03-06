# Contributing

## Setup

```bash
uv sync --dev
```

## Commands

```bash
uv run pytest          # run all tests
uv run pytest -v       # run tests with verbose output
uv run main.py sample.pptx --dry-run  # smoke test
```

## Architecture

4-step pipeline: **read** the `.pptx` (zip), **compress** each media file, **patch** relationship XML if a file is renamed, **write** a new zip as `<stem>_compressed.pptx`.

```
main.py          CLI (argparse) → calls compress_pptx(), prints report
src/
  compress.py    Core orchestration: opens input zip, iterates entries,
                 routes media to images.py or videos.py, writes output zip.
                 Patches [Content_Types].xml and all .rels files when a
                 file is renamed (e.g. .png → .jpg, .avi → .mp4).
  images.py      compress_image() — Pillow JPEG recompression + resize.
                 RGBA/palette modes are composited onto white before JPEG save.
  videos.py      compress_video() — ffmpeg subprocess via imageio_ffmpeg.
                 Always outputs .mp4.
  quality.py     QualityPreset dataclass + PRESETS dict (high/medium/low).
  report.py      ItemResult, Report, print_summary(). Tracks per-item and
                 aggregate size before/after.
tests/
  conftest.py    Fixtures: synthetic .pptx built with zipfile + Pillow in memory.
```

### Key behaviours

- `compress_image` and `compress_video` return the **original bytes unchanged** if savings are < 5%, or if ffmpeg fails.
- `[Content_Types].xml` is patched after compression to declare any new media extensions (e.g. `jpg` when PNGs are converted).
- All `.rels` files are scanned for media references when a file is renamed, not just `ppt/slides/_rels/`.
- `ffmpeg` is bundled via `imageio-ffmpeg` — no system install required.
- `pythonpath = ["src", "."]` in `pyproject.toml` makes `src/` modules importable during tests.

## Building a standalone executable

```bash
uv run python build.py   # outputs dist/compwesr (or dist/compwesr.exe on Windows)
```

CI builds for all three platforms are triggered by pushing a `v*` tag, which also publishes a GitHub release automatically.
