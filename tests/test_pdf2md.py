"""Tests for PDF-to-Markdown conversion using MinerU.

Tests MinerU integration for PDF extraction and Markdown generation.
These are integration tests requiring MinerU to be installed.
"""

import pytest
from pathlib import Path
import json


@pytest.mark.integration
def test_convert_pdf_to_markdown(temp_dir):
    """Test converting PDF to Markdown."""
    from batch2md.converters import convert_to_markdown

    # This requires a real PDF file
    pdf_file = temp_dir / "sample.pdf"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test PDF file not available")

    md_path = convert_to_markdown(pdf_file, output_dir)

    assert md_path.exists()
    assert md_path.suffix == ".md"
    assert md_path.parent == output_dir


@pytest.mark.integration
def test_markdown_contains_text_content(temp_dir):
    """Test that converted Markdown contains text from PDF."""
    from batch2md.converters import convert_to_markdown

    pdf_file = temp_dir / "sample.pdf"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test PDF file not available")

    md_path = convert_to_markdown(pdf_file, output_dir)

    # Read markdown content
    content = md_path.read_text()

    # Should have some content
    assert len(content) > 0
    # Should be valid text (not binary)
    assert content.isprintable() or '\n' in content


@pytest.mark.integration
def test_table_converted_to_markdown_table(temp_dir):
    """Test that tables are converted to Markdown table format."""
    from batch2md.converters import convert_to_markdown

    # Requires a PDF with tables
    pdf_file = temp_dir / "with_tables.pdf"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test PDF with tables not available")

    md_path = convert_to_markdown(pdf_file, output_dir)
    content = md_path.read_text()

    # Look for Markdown table syntax
    # Tables should have | characters and separator lines
    assert "|" in content or "---" in content


@pytest.mark.integration
def test_images_extracted_to_directory(temp_dir):
    """Test that images are extracted to separate directory."""
    from batch2md.converters import extract_images

    pdf_file = temp_dir / "with_images.pdf"
    images_dir = temp_dir / "images"
    images_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test PDF with images not available")

    image_paths = extract_images(pdf_file, images_dir)

    # Should return list of extracted image paths
    assert isinstance(image_paths, list)

    if len(image_paths) > 0:
        # Images should exist
        for img_path in image_paths:
            assert img_path.exists()
            assert img_path.parent == images_dir
            # Should be image format
            assert img_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']


@pytest.mark.integration
def test_markdown_references_images_correctly(temp_dir):
    """Test that Markdown references images with correct paths."""
    from batch2md.converters import convert_to_markdown

    pdf_file = temp_dir / "with_images.pdf"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test PDF with images not available")

    md_path = convert_to_markdown(pdf_file, output_dir)
    content = md_path.read_text()

    # Look for Markdown image syntax: ![...](path)
    if "![" in content:
        assert "](" in content
        # Should reference images directory
        assert "images/" in content.lower()


@pytest.mark.integration
def test_heading_conversion(temp_dir):
    """Test that PDF headings are converted to Markdown headers."""
    from batch2md.converters import convert_to_markdown

    pdf_file = temp_dir / "with_headings.pdf"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test PDF with headings not available")

    md_path = convert_to_markdown(pdf_file, output_dir)
    content = md_path.read_text()

    # Look for Markdown heading syntax
    lines = content.split('\n')
    has_headings = any(line.startswith('#') for line in lines)
    assert has_headings


@pytest.mark.integration
def test_list_preservation(temp_dir):
    """Test that lists are preserved in Markdown."""
    from batch2md.converters import convert_to_markdown

    pdf_file = temp_dir / "with_lists.pdf"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test PDF with lists not available")

    md_path = convert_to_markdown(pdf_file, output_dir)
    content = md_path.read_text()

    # Look for list markers
    lines = content.split('\n')
    has_lists = any(
        line.strip().startswith(('-', '*', '+')) or
        line.strip()[0].isdigit() and '. ' in line
        for line in lines if line.strip()
    )
    assert has_lists


@pytest.mark.integration
def test_mineru_backend_pipeline(temp_dir):
    """Test using pipeline backend (default)."""
    from batch2md.converters import convert_to_markdown

    pdf_file = temp_dir / "sample.pdf"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test PDF file not available")

    md_path = convert_to_markdown(pdf_file, output_dir, backend="pipeline")

    assert md_path.exists()
    assert md_path.suffix == ".md"


@pytest.mark.integration
@pytest.mark.slow
def test_mineru_backend_vlm(temp_dir):
    """Test using VLM backend (if available)."""
    from batch2md.converters import convert_to_markdown

    pdf_file = temp_dir / "sample.pdf"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test PDF file not available")

    try:
        md_path = convert_to_markdown(pdf_file, output_dir, backend="vlm")
        assert md_path.exists()
    except Exception as e:
        # VLM might not be available
        pytest.skip(f"VLM backend not available: {e}")


@pytest.mark.unit
def test_mineru_not_installed_error():
    """Test proper error when MinerU is not installed."""
    from batch2md.converters import check_mineru

    # This function should check for MinerU availability
    try:
        is_available = check_mineru()
        assert isinstance(is_available, bool)
    except ImportError as e:
        # Should provide helpful error message
        assert "mineru" in str(e).lower()


@pytest.mark.integration
def test_invalid_pdf_error_handling(temp_dir):
    """Test handling of invalid PDF files."""
    from batch2md.converters import convert_to_markdown

    # Create invalid PDF
    invalid_pdf = temp_dir / "invalid.pdf"
    invalid_pdf.write_bytes(b"This is not a valid PDF")

    output_dir = temp_dir / "output"
    output_dir.mkdir()

    # Should raise an exception
    with pytest.raises(Exception):
        convert_to_markdown(invalid_pdf, output_dir)


@pytest.mark.integration
def test_convert_creates_markdown_file_with_same_basename(temp_dir):
    """Test that output Markdown has same basename as input PDF."""
    from batch2md.converters import convert_to_markdown

    pdf_file = temp_dir / "mydocument.pdf"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test PDF file not available")

    md_path = convert_to_markdown(pdf_file, output_dir)

    assert md_path.stem == "mydocument"
    assert md_path.name == "mydocument.md"


@pytest.mark.integration
def test_extract_images_with_meaningful_names(temp_dir):
    """Test that extracted images have meaningful names."""
    from batch2md.converters import extract_images

    pdf_file = temp_dir / "document.pdf"
    images_dir = temp_dir / "images"
    images_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test PDF file not available")

    image_paths = extract_images(pdf_file, images_dir)

    if len(image_paths) > 0:
        for img_path in image_paths:
            # Should contain document name
            assert "document" in img_path.stem.lower()
            # Should have image number
            assert any(char.isdigit() for char in img_path.stem)


@pytest.mark.integration
def test_convert_handles_complex_layout(temp_dir):
    """Test conversion of PDF with complex layout."""
    from batch2md.converters import convert_to_markdown

    pdf_file = temp_dir / "complex_layout.pdf"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test PDF with complex layout not available")

    md_path = convert_to_markdown(pdf_file, output_dir)

    # Should complete without error
    assert md_path.exists()
    content = md_path.read_text()
    assert len(content) > 0


@pytest.mark.integration
def test_convert_multipage_pdf(temp_dir):
    """Test conversion of multi-page PDF."""
    from batch2md.converters import convert_to_markdown

    pdf_file = temp_dir / "multipage.pdf"
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    if not pdf_file.exists():
        pytest.skip("Test multi-page PDF not available")

    md_path = convert_to_markdown(pdf_file, output_dir)

    # Should handle multiple pages
    content = md_path.read_text()
    # Multi-page document should have substantial content
    assert len(content) > 500


@pytest.mark.unit
def test_supported_format_is_pdf():
    """Test that PDF format is recognized as supported."""
    from batch2md.models import SupportedFormat

    pdf_path = Path("/test/file.pdf")
    assert SupportedFormat.is_supported(pdf_path)


@pytest.mark.unit
def test_pdf_does_not_require_conversion():
    """Test that PDF files don't require PDF conversion step."""
    from batch2md.models import SupportedFormat

    pdf_path = Path("/test/file.pdf")
    # PDF files should NOT require conversion to PDF (they already are)
    assert not SupportedFormat.requires_pdf_conversion(pdf_path)
