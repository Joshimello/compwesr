# compwesr

Compress images and videos embedded in `.pptx` files, reducing file size while preserving layout, positions, playback settings, and file integrity.

## Download

Pre-built binaries are available on the [releases page](https://github.com/Joshimello/compwesr/releases/latest):

| Platform | File |
|----------|------|
| macOS | `compwesr-macos.tar.gz` |
| Linux | `compwesr-linux.tar.gz` |
| Windows | `compwesr-windows.zip` |

Extract and run — no Python or ffmpeg installation needed.

## Usage

```
compwesr <file.pptx> [options]
```

| Flag | Description |
|------|-------------|
| `--quality high\|medium\|low` | Compression preset (default: `medium`) |
| `--images-only` | Skip video compression |
| `--videos-only` | Skip image compression |
| `--dry-run` | Analyze without writing output |
| `--backup` | Save a copy of the original as `<name>_backup.pptx` |

### Examples

```bash
# Compress with medium quality (default)
compwesr deck.pptx

# Aggressive compression, images only
compwesr deck.pptx --quality low --images-only

# Preview savings without writing
compwesr deck.pptx --dry-run
```

### Output

```
Reading deck.pptx...
Compressing deck.pptx...
  Images: 12 compressed (4.2 MB → 1.1 MB)
  Videos: 3 compressed (80 MB → 22 MB)
Saved: deck_compressed.pptx (84 MB → 23.3 MB, -72%)
```

The output is always written as `<original>_compressed.pptx`. The input file is never modified.

## Quality Presets

| Preset | JPEG quality | Max height | Video CRF |
|--------|-------------|------------|-----------|
| `high` | 85 | 1080p | 23 |
| `medium` | 70 | 720p | 28 |
| `low` | 50 | 480p | 32 |
