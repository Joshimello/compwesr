import shutil
import tempfile
import zipfile
from pathlib import Path

from images import IMAGE_EXTS, compress_image
from quality import QualityPreset
from report import ItemResult, Report
from videos import VIDEO_EXTS, compress_video


def _patch_rels_for_rename(rels_xml: bytes, old_name: str, new_name: str) -> bytes:
    """Replace media target in relationship XML when a file is renamed."""
    old = f'Target="../media/{old_name}"'.encode()
    new = f'Target="../media/{new_name}"'.encode()
    return rels_xml.replace(old, new)


def compress_pptx(
    input_path: Path,
    preset: QualityPreset,
    images_only: bool = False,
    videos_only: bool = False,
    dry_run: bool = False,
    backup: bool = False,
) -> Report:
    stem = input_path.stem
    output_path = input_path.with_name(f"{stem}_compressed.pptx")

    report = Report(
        input_path=str(input_path),
        output_path=str(output_path),
    )

    has_videos = not images_only

    if backup:
        backup_path = input_path.with_name(f"{stem}_backup.pptx")
        shutil.copy2(input_path, backup_path)

    # Accumulate rels patches: {rels_zip_path: bytes}
    rels_patches: dict[str, bytes] = {}

    # We do two passes: first collect entries, then write.
    # Store processed entries in memory.
    entries: dict[str, bytes] = {}

    with zipfile.ZipFile(input_path, "r") as zin:
        all_names = zin.namelist()

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)

            for name in all_names:
                data = zin.read(name)
                lower = name.lower()

                if not lower.startswith("ppt/media/"):
                    entries[name] = data
                    continue

                filename = name.split("/")[-1]
                ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

                if ext in IMAGE_EXTS and not videos_only:
                    compressed, new_filename = compress_image(data, preset, filename)
                    item = ItemResult(
                        name=filename,
                        kind="image",
                        original_size=len(data),
                        compressed_size=len(compressed),
                        skipped=(compressed is data),
                    )
                    report.add(item)

                    new_name = f"ppt/media/{new_filename}"
                    entries[new_name] = compressed
                    if new_filename != filename:
                        _queue_rels_rename(rels_patches, all_names, zin, filename, new_filename)

                elif ext in VIDEO_EXTS and not images_only and has_videos:
                    compressed, new_filename = compress_video(data, preset, filename, tmp_dir)
                    item = ItemResult(
                        name=filename,
                        kind="video",
                        original_size=len(data),
                        compressed_size=len(compressed),
                        skipped=(compressed is data),
                    )
                    report.add(item)

                    new_name = f"ppt/media/{new_filename}"
                    entries[new_name] = compressed
                    if new_filename != filename:
                        _queue_rels_rename(rels_patches, all_names, zin, filename, new_filename)

                else:
                    entries[name] = data
                    report.original_total += len(data)
                    report.compressed_total += len(data)

    # Apply rels patches
    for rels_path, patched in rels_patches.items():
        entries[rels_path] = patched

    if not dry_run:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for name, data in entries.items():
                zout.writestr(name, data)

    return report


def _queue_rels_rename(
    rels_patches: dict[str, bytes],
    all_names: list[str],
    zin: zipfile.ZipFile,
    old_name: str,
    new_name: str,
) -> None:
    """Find and patch all rels files that reference old_name."""
    for entry in all_names:
        if entry.startswith("ppt/slides/_rels/") and entry.endswith(".rels"):
            current = rels_patches.get(entry) or zin.read(entry)
            target = f'Target="../media/{old_name}"'.encode()
            if target in current:
                rels_patches[entry] = _patch_rels_for_rename(current, old_name, new_name)
