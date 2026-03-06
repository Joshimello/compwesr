import argparse
import sys
from pathlib import Path

from compress import compress_pptx
from quality import DEFAULT_PRESET, PRESETS
from report import print_summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compress images and videos embedded in .pptx files."
    )
    parser.add_argument("input", help="Path to the .pptx file to compress")
    parser.add_argument(
        "--quality",
        choices=list(PRESETS),
        default=DEFAULT_PRESET,
        help=f"Compression quality preset (default: {DEFAULT_PRESET})",
    )
    parser.add_argument("--images-only", action="store_true", help="Only compress images")
    parser.add_argument("--videos-only", action="store_true", help="Only compress videos")
    parser.add_argument("--dry-run", action="store_true", help="Analyze without writing output")
    parser.add_argument("--backup", action="store_true", help="Save a backup of the original")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    if input_path.suffix.lower() != ".pptx":
        print(f"Error: expected a .pptx file, got: {input_path.suffix}", file=sys.stderr)
        sys.exit(1)

    preset = PRESETS[args.quality]

    print(f"Reading {input_path.name}...", flush=True)

    try:
        report = compress_pptx(
            input_path=input_path,
            preset=preset,
            images_only=args.images_only,
            videos_only=args.videos_only,
            dry_run=args.dry_run,
            backup=args.backup,
        )
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print_summary(report, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
