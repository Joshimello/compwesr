# compwesr

Compress images and videos embedded in `.pptx` files, reducing file size while preserving layout, positions, playback settings, and file integrity.

## Download

Pre-built binaries are available on the [releases page](https://github.com/Joshimello/compwesr/releases/latest):

| Platform | File |
|----------|------|
| macOS | `compwesr-macos.tar.gz` |
| Linux | `compwesr-linux.tar.gz` |
| Windows | `compwesr-windows.zip` |

Extract and run — no installation needed.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

`ffmpeg` is bundled automatically via `imageio-ffmpeg` — no system install needed.

## Installation

```bash
uv sync
```

## Usage

```bash
uv run python main.py deck.pptx [options]
```

### Options

| Flag | Description |
|------|-------------|
| `--quality high\|medium\|low` | Compression preset (default: `medium`) |
| `--images-only` | Skip video compression |
| `--videos-only` | Skip image compression |
| `--dry-run` | Analyze without writing output |
| `--backup` | Save a copy of the original as `<name>_backup.pptx` |

### Example

```bash
# Compress with medium quality (default)
uv run python main.py deck.pptx

# Aggressive compression, images only
uv run python main.py deck.pptx --quality low --images-only

# Preview savings without writing
uv run python main.py deck.pptx --dry-run
```

### Output

```
Compressing deck.pptx...
  Images: 12 compressed (4.2 MB → 1.1 MB)
  Videos: 3 compressed (80 MB → 22 MB)
Saved: deck_compressed.pptx (84 MB → 23.3 MB, -72%)
```

The output file is always written as `<original>_compressed.pptx`. The input file is never modified.

## Quality Presets

| Preset | JPEG quality | Max video height | Video CRF |
|--------|-------------|-----------------|-----------|
| `high` | 85 | 1080p | 23 |
| `medium` | 70 | 720p | 28 |
| `low` | 50 | 480p | 32 |

## Building a standalone executable

```bash
uv run python build.py   # outputs dist/compwesr (or dist/compwesr.exe on Windows)
```

## Development

```bash
# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Run tests with output
uv run pytest -v
```

## Project structure

```
src/
  quality.py    # Quality presets
  report.py     # Result tracking and summary output
  images.py     # Image compression via Pillow
  videos.py     # Video compression via ffmpeg
  compress.py   # Core zip-level orchestration
main.py         # CLI entry point
tests/
```
