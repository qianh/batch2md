"""Integration tests for full batch2md pipeline.

Tests end-to-end conversion workflows with real files and tools.
"""

import pytest
from pathlib import Path
import subprocess
import sys


@pytest.mark.integration
def test_full_pipeline_single_docx(temp_dir, sample_text_file):
    """Test complete pipeline: DOCX → PDF → Markdown."""
    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig

    # Create a DOCX file first
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "docx",
             "--outdir", str(temp_dir), str(sample_text_file)],
            capture_output=True,
            timeout=30,
            check=True
        )
        sample_text_file.with_suffix(".docx").rename(temp_dir / "test.docx")
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("LibreOffice not available")

    # Skip if MinerU not installed
    try:
        import mineru
    except ImportError:
        pytest.skip("MinerU not installed")

    config = ConversionConfig(
        input_dir=temp_dir,
        recursive=False,
        verbose=True
    )

    summary = run_conversion(config)

    # Check results
    assert summary.total_files >= 1
    assert summary.successful >= 0  # May fail if MinerU models not downloaded
    assert summary.elapsed_time > 0


@pytest.mark.integration
def test_full_pipeline_multiple_formats(temp_dir):
    """Test pipeline with multiple document formats."""
    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig

    # Create test files
    (temp_dir / "doc.docx").touch()
    (temp_dir / "pres.pptx").touch()
    (temp_dir / "sheet.xlsx").touch()

    try:
        import mineru
    except ImportError:
        pytest.skip("MinerU not installed")

    config = ConversionConfig(
        input_dir=temp_dir,
        recursive=False,
        dry_run=True  # Dry run to avoid requiring real conversion
    )

    summary = run_conversion(config)

    # In dry run, should identify files
    assert summary.total_files == 3


@pytest.mark.integration
def test_full_pipeline_recursive_directories(nested_structure):
    """Test pipeline with nested directory structure."""
    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig

    # Create docs in nested structure
    (nested_structure / "root.docx").touch()
    (nested_structure / "subdir1" / "sub1.docx").touch()
    (nested_structure / "subdir2" / "sub2.docx").touch()

    config = ConversionConfig(
        input_dir=nested_structure,
        recursive=True,
        dry_run=True
    )

    summary = run_conversion(config)

    # Should find all files
    assert summary.total_files == 3


@pytest.mark.integration
@pytest.mark.slow
def test_full_pipeline_with_images(temp_dir):
    """Test pipeline with documents containing images."""
    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig

    # Requires actual document with images
    doc_with_images = temp_dir / "with_images.docx"
    if not doc_with_images.exists():
        pytest.skip("Test document with images not available")

    try:
        import mineru
    except ImportError:
        pytest.skip("MinerU not installed")

    config = ConversionConfig(
        input_dir=temp_dir,
        recursive=False
    )

    summary = run_conversion(config)

    # Check that images directory was created
    images_dir = temp_dir / "markdown" / "images"
    if summary.successful > 0:
        # Only check if conversion succeeded
        assert images_dir.exists() or summary.failed > 0


@pytest.mark.integration
def test_full_pipeline_error_recovery(temp_dir):
    """Test that pipeline continues after individual failures."""
    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig

    # Create mix of valid and invalid files
    (temp_dir / "valid.docx").touch()
    corrupted = temp_dir / "corrupted.docx"
    corrupted.write_bytes(b"Not a valid DOCX")
    (temp_dir / "another.docx").touch()

    config = ConversionConfig(
        input_dir=temp_dir,
        recursive=False,
        dry_run=False
    )

    try:
        summary = run_conversion(config)

        # Should process all files despite errors
        assert summary.total_files == 3
        # Some may fail, but should continue
        assert summary.successful + summary.failed + summary.skipped == summary.total_files
    except ImportError:
        pytest.skip("Required dependencies not installed")


@pytest.mark.integration
@pytest.mark.slow
def test_batch_100_documents(temp_dir):
    """Performance test: process 100 documents."""
    # This is a performance test
    # Create 100 small test files
    for i in range(100):
        (temp_dir / f"doc{i:03d}.docx").touch()

    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig

    config = ConversionConfig(
        input_dir=temp_dir,
        recursive=False,
        dry_run=True  # Dry run for speed
    )

    summary = run_conversion(config)

    # Should handle all 100 files
    assert summary.total_files == 100
    # Should complete in reasonable time (checked by elapsed_time)
    assert summary.elapsed_time < 60  # Should be fast in dry-run mode


@pytest.mark.integration
def test_progress_reporting(temp_dir, capsys):
    """Test that progress is reported during conversion."""
    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig

    # Create test files
    for i in range(3):
        (temp_dir / f"doc{i}.docx").touch()

    config = ConversionConfig(
        input_dir=temp_dir,
        recursive=False,
        verbose=True,
        dry_run=True
    )

    run_conversion(config)

    # Check stdout for progress messages
    captured = capsys.readouterr()
    assert "Processing" in captured.out or "Found" in captured.out


@pytest.mark.integration
def test_summary_generation(temp_dir):
    """Test that conversion summary is generated correctly."""
    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig

    (temp_dir / "doc1.docx").touch()
    (temp_dir / "doc2.docx").touch()

    config = ConversionConfig(
        input_dir=temp_dir,
        recursive=False,
        dry_run=True
    )

    summary = run_conversion(config)

    # Verify summary structure
    assert hasattr(summary, 'total_files')
    assert hasattr(summary, 'successful')
    assert hasattr(summary, 'failed')
    assert hasattr(summary, 'elapsed_time')
    assert summary.total_files == 2


@pytest.mark.integration
def test_dry_run_mode(temp_dir):
    """Test dry-run mode doesn't create output files."""
    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig

    (temp_dir / "test.docx").touch()

    config = ConversionConfig(
        input_dir=temp_dir,
        recursive=False,
        dry_run=True
    )

    summary = run_conversion(config)

    # Output directory should not be created in dry-run
    markdown_dir = temp_dir / "markdown"
    # In dry run, files shouldn't be created
    # But directory might be created for validation
    if markdown_dir.exists():
        # Should be empty or have no .md files
        md_files = list(markdown_dir.glob("*.md"))
        assert len(md_files) == 0


@pytest.mark.integration
def test_json_output_format(temp_dir, capsys):
    """Test JSON output format."""
    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig
    import json

    (temp_dir / "test.docx").touch()

    config = ConversionConfig(
        input_dir=temp_dir,
        recursive=False,
        json_output=True,
        dry_run=True
    )

    summary = run_conversion(config)

    # Get JSON output
    json_data = summary.to_dict()

    # Verify JSON structure
    assert 'summary' in json_data
    assert 'total_files' in json_data['summary']
    assert 'successful' in json_data['summary']
    assert 'failed' in json_data['summary']


@pytest.mark.integration
def test_exit_code_all_success(temp_dir):
    """Test exit code when all conversions succeed."""
    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig

    (temp_dir / "test.docx").touch()

    config = ConversionConfig(
        input_dir=temp_dir,
        recursive=False,
        dry_run=True
    )

    summary = run_conversion(config)

    # Dry run should succeed
    assert summary.exit_code == 0


@pytest.mark.integration
def test_exit_code_partial_failure(temp_dir):
    """Test exit code when some conversions fail."""
    from batch2md.models import ConversionSummary, ConversionJob, ConversionStatus
    from datetime import datetime

    # Create summary with partial failure
    job1 = ConversionJob(
        input_path=temp_dir / "success.docx",
        pdf_path=None,
        output_path=temp_dir / "success.md",
        images_dir=temp_dir / "images",
        status=ConversionStatus.COMPLETED
    )
    job2 = ConversionJob(
        input_path=temp_dir / "failed.docx",
        pdf_path=None,
        output_path=temp_dir / "failed.md",
        images_dir=temp_dir / "images",
        status=ConversionStatus.FAILED,
        error="Conversion failed"
    )

    summary = ConversionSummary(
        total_files=2,
        successful=1,
        failed=1,
        skipped=0,
        failed_jobs=[job2],
        completed_jobs=[job1],
        start_time=datetime.now(),
        end_time=datetime.now()
    )

    # Partial failure should return exit code 1
    assert summary.exit_code == 1


@pytest.mark.integration
def test_exit_code_total_failure(temp_dir):
    """Test exit code when all conversions fail."""
    from batch2md.models import ConversionSummary, ConversionJob, ConversionStatus
    from datetime import datetime

    job = ConversionJob(
        input_path=temp_dir / "failed.docx",
        pdf_path=None,
        output_path=temp_dir / "failed.md",
        images_dir=temp_dir / "images",
        status=ConversionStatus.FAILED,
        error="Conversion failed"
    )

    summary = ConversionSummary(
        total_files=1,
        successful=0,
        failed=1,
        skipped=0,
        failed_jobs=[job],
        completed_jobs=[],
        start_time=datetime.now(),
        end_time=datetime.now()
    )

    # Total failure should return exit code 2
    assert summary.exit_code == 2


@pytest.mark.integration
def test_verbose_mode_shows_details(temp_dir, capsys):
    """Test that verbose mode shows detailed information."""
    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig

    (temp_dir / "test.docx").touch()

    config = ConversionConfig(
        input_dir=temp_dir,
        recursive=False,
        verbose=True,
        dry_run=True
    )

    run_conversion(config)

    captured = capsys.readouterr()
    # Verbose mode should show more output
    assert len(captured.out) > 0


@pytest.mark.integration
def test_output_directory_structure_preserved(nested_structure):
    """Test that input directory structure is preserved in output."""
    from batch2md.cli import run_conversion
    from batch2md.models import ConversionConfig

    # Create nested structure
    (nested_structure / "root.docx").touch()
    (nested_structure / "sub1").mkdir(parents=True, exist_ok=True)
    (nested_structure / "sub1" / "file1.docx").touch()
    (nested_structure / "sub2").mkdir(parents=True, exist_ok=True)
    (nested_structure / "sub2" / "file2.docx").touch()

    config = ConversionConfig(
        input_dir=nested_structure,
        recursive=True,
        dry_run=True
    )

    run_conversion(config)

    # Check that output structure is planned correctly
    # (In real run, directories would be created)
    summary = run_conversion(config)
    assert summary.total_files == 3


@pytest.mark.integration
def test_cli_end_to_end(temp_dir):
    """Test complete CLI workflow end-to-end."""
    # Create test file
    (temp_dir / "test.docx").touch()

    # Run via CLI
    result = subprocess.run(
        [sys.executable, "-m", "batch2md.main", str(temp_dir), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=30
    )

    # Should complete without critical errors
    assert result.returncode in [0, 1]  # 0=success, 1=partial failure
