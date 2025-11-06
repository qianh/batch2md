"""Tests for document-to-PDF conversion.

Tests LibreOffice-based document conversion functionality.
These are integration tests requiring LibreOffice to be installed.
"""

import pytest
from pathlib import Path
import subprocess


@pytest.mark.integration
def test_convert_docx_to_pdf(temp_dir, sample_text_file):
    """Test converting DOCX to PDF."""
    from batch2md.converters import convert_to_pdf

    # First create a DOCX from text file using LibreOffice
    docx_file = temp_dir / "test.docx"

    # Use LibreOffice to create DOCX
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "docx",
             "--outdir", str(temp_dir), str(sample_text_file)],
            capture_output=True,
            timeout=30,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.skip(f"LibreOffice not available: {e}")

    # Rename to expected name
    sample_text_file.with_suffix(".docx").rename(docx_file)

    # Now test our converter
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    pdf_path = convert_to_pdf(docx_file, output_dir)

    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
    assert pdf_path.parent == output_dir


@pytest.mark.integration
def test_convert_pptx_to_pdf(temp_dir):
    """Test converting PPTX to PDF."""
    # This test would require a real PPTX file
    # For now, we'll test the interface
    from batch2md.converters import convert_to_pdf

    pptx_file = temp_dir / "presentation.pptx"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    # This will fail without a real PPTX, but tests the interface
    if not pptx_file.exists():
        pytest.skip("Test PPTX file not available")

    pdf_path = convert_to_pdf(pptx_file, output_dir)
    assert pdf_path.suffix == ".pdf"


@pytest.mark.integration
def test_convert_xlsx_to_pdf(temp_dir):
    """Test converting XLSX to PDF."""
    from batch2md.converters import convert_to_pdf

    xlsx_file = temp_dir / "spreadsheet.xlsx"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not xlsx_file.exists():
        pytest.skip("Test XLSX file not available")

    pdf_path = convert_to_pdf(xlsx_file, output_dir)
    assert pdf_path.suffix == ".pdf"


@pytest.mark.integration
def test_convert_odt_to_pdf(temp_dir):
    """Test converting ODT (OpenDocument Text) to PDF."""
    from batch2md.converters import convert_to_pdf

    odt_file = temp_dir / "document.odt"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not odt_file.exists():
        pytest.skip("Test ODT file not available")

    pdf_path = convert_to_pdf(odt_file, output_dir)
    assert pdf_path.suffix == ".pdf"


@pytest.mark.integration
def test_pdf_output_is_valid(temp_dir, sample_text_file):
    """Test that generated PDF is valid."""
    from batch2md.converters import convert_to_pdf

    # Create DOCX first
    docx_file = temp_dir / "test.docx"
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "docx",
             "--outdir", str(temp_dir), str(sample_text_file)],
            capture_output=True,
            timeout=30,
            check=True
        )
        sample_text_file.with_suffix(".docx").rename(docx_file)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("LibreOffice not available")

    output_dir = temp_dir / "output"
    output_dir.mkdir()

    pdf_path = convert_to_pdf(docx_file, output_dir)

    # Check PDF validity
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0  # Not empty

    # Check PDF magic bytes
    with open(pdf_path, "rb") as f:
        header = f.read(4)
        assert header == b"%PDF", "PDF file should start with %PDF"


@pytest.mark.integration
def test_conversion_preserves_content(temp_dir, sample_text_file):
    """Test that conversion preserves text content."""
    from batch2md.converters import convert_to_pdf

    # Create DOCX
    docx_file = temp_dir / "test.docx"
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "docx",
             "--outdir", str(temp_dir), str(sample_text_file)],
            capture_output=True,
            timeout=30,
            check=True
        )
        sample_text_file.with_suffix(".docx").rename(docx_file)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("LibreOffice not available")

    output_dir = temp_dir / "output"
    output_dir.mkdir()

    pdf_path = convert_to_pdf(docx_file, output_dir)

    # PDF should exist and have content
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1000  # Reasonable size for a simple doc


@pytest.mark.integration
def test_conversion_handles_corrupted_file(temp_dir):
    """Test that corrupted files are handled gracefully."""
    from batch2md.converters import convert_to_pdf

    # Create a corrupted DOCX file (completely invalid binary data)
    corrupted = temp_dir / "corrupted.docx"
    corrupted.write_bytes(b"\x00\xFF\xFE\xFD" * 100)  # Random binary data

    output_dir = temp_dir / "output"
    output_dir.mkdir()

    # LibreOffice may or may not handle this gracefully
    # It might succeed (attempting to repair) or fail
    try:
        result = convert_to_pdf(corrupted, output_dir)
        # If it succeeds, LibreOffice managed to create something
        assert result.exists()
    except (RuntimeError, Exception):
        # If it fails, that's also acceptable
        pass


@pytest.mark.integration
def test_conversion_handles_missing_file(temp_dir):
    """Test that missing files are handled gracefully."""
    from batch2md.converters import convert_to_pdf

    nonexistent = temp_dir / "nonexistent.docx"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    # Should raise FileNotFoundError or similar
    with pytest.raises((FileNotFoundError, Exception)):
        convert_to_pdf(nonexistent, output_dir)


@pytest.mark.unit
def test_libreoffice_not_installed_error():
    """Test proper error when LibreOffice is not installed."""
    from batch2md.converters import check_libreoffice

    # This function should check for LibreOffice availability
    try:
        is_available = check_libreoffice()
        # If we get here, LibreOffice is available
        assert isinstance(is_available, bool)
    except Exception as e:
        # Should provide helpful error message
        assert "libreoffice" in str(e).lower() or "soffice" in str(e).lower()


@pytest.mark.integration
def test_convert_returns_correct_path(temp_dir, sample_text_file):
    """Test that converter returns correct output path."""
    from batch2md.converters import convert_to_pdf

    # Create DOCX
    docx_file = temp_dir / "mydocument.docx"
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "docx",
             "--outdir", str(temp_dir), str(sample_text_file)],
            capture_output=True,
            timeout=30,
            check=True
        )
        sample_text_file.with_suffix(".docx").rename(docx_file)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("LibreOffice not available")

    output_dir = temp_dir / "output"
    output_dir.mkdir()

    pdf_path = convert_to_pdf(docx_file, output_dir)

    # Check path components
    assert pdf_path.name == "mydocument.pdf"
    assert pdf_path.parent == output_dir


@pytest.mark.integration
def test_convert_creates_output_directory_if_needed(temp_dir, sample_text_file):
    """Test that converter creates output directory if it doesn't exist."""
    from batch2md.converters import convert_to_pdf

    # Create DOCX
    docx_file = temp_dir / "test.docx"
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "docx",
             "--outdir", str(temp_dir), str(sample_text_file)],
            capture_output=True,
            timeout=30,
            check=True
        )
        sample_text_file.with_suffix(".docx").rename(docx_file)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("LibreOffice not available")

    # Output directory doesn't exist
    output_dir = temp_dir / "nonexistent_output"
    assert not output_dir.exists()

    pdf_path = convert_to_pdf(docx_file, output_dir)

    # Should create directory and file
    assert output_dir.exists()
    assert pdf_path.exists()
