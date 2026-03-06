import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import main as cli_module


def run_main(args: list[str]) -> int:
    with patch("sys.argv", ["main.py"] + args):
        try:
            cli_module.main()
            return 0
        except SystemExit as e:
            return int(e.code) if e.code is not None else 0


def test_cli_basic_run(sample_pptx_path):
    rc = run_main([str(sample_pptx_path), "--quality", "low"])
    assert rc == 0
    output = sample_pptx_path.with_name("sample_compressed.pptx")
    assert output.exists()


def test_cli_output_not_larger_than_input(sample_pptx_path):
    run_main([str(sample_pptx_path), "--quality", "low"])
    output = sample_pptx_path.with_name("sample_compressed.pptx")
    assert output.stat().st_size <= sample_pptx_path.stat().st_size * 1.05


def test_cli_dry_run_no_output(sample_pptx_path):
    rc = run_main([str(sample_pptx_path), "--dry-run"])
    assert rc == 0
    output = sample_pptx_path.with_name("sample_compressed.pptx")
    assert not output.exists()


def test_cli_missing_file(tmp_path, capsys):
    rc = run_main([str(tmp_path / "nonexistent.pptx")])
    assert rc != 0


def test_cli_wrong_extension(tmp_path, capsys):
    p = tmp_path / "deck.docx"
    p.write_bytes(b"not a pptx")
    rc = run_main([str(p)])
    assert rc != 0


def test_cli_default_quality(sample_pptx_path):
    """Default quality is medium — should work without --quality flag."""
    rc = run_main([str(sample_pptx_path)])
    assert rc == 0


def test_cli_images_only(sample_pptx_path):
    rc = run_main([str(sample_pptx_path), "--images-only"])
    assert rc == 0


def test_cli_backup_created(sample_pptx_path):
    run_main([str(sample_pptx_path), "--backup"])
    backup = sample_pptx_path.with_name("sample_backup.pptx")
    assert backup.exists()


def test_cli_print_output(sample_pptx_path, capsys):
    run_main([str(sample_pptx_path), "--quality", "low"])
    out = capsys.readouterr().out
    assert "Compressing" in out
    assert "Saved:" in out
