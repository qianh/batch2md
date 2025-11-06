"""Tests for output path management and file organization.

Tests output directory creation, path resolution, and conflict handling.
"""

import pytest
from pathlib import Path
from datetime import datetime
import time


@pytest.mark.unit
def test_resolve_output_path_basic(temp_dir):
    """Test basic output path resolution."""
    from batch2md.output_manager import resolve_output_path

    input_file = temp_dir / "document.docx"
    output_dir = temp_dir / "markdown"
    base_dir = temp_dir

    result = resolve_output_path(input_file, output_dir, base_dir)

    assert result == output_dir / "document.md"


@pytest.mark.unit
def test_preserve_subdirectory_structure(temp_dir):
    """Test that subdirectory structure is preserved in output."""
    from batch2md.output_manager import resolve_output_path

    input_file = temp_dir / "subdir" / "nested" / "document.docx"
    output_dir = temp_dir / "markdown"
    base_dir = temp_dir

    result = resolve_output_path(input_file, output_dir, base_dir)

    expected = output_dir / "subdir" / "nested" / "document.md"
    assert result == expected


@pytest.mark.unit
def test_timestamp_suffix_on_conflict(temp_dir):
    """Test that timestamp suffix is added when file exists."""
    from batch2md.output_manager import resolve_output_path

    input_file = temp_dir / "document.docx"
    output_dir = temp_dir / "markdown"
    base_dir = temp_dir

    # Create existing file
    output_dir.mkdir(parents=True)
    existing = output_dir / "document.md"
    existing.write_text("existing content")

    result = resolve_output_path(input_file, output_dir, base_dir, overwrite=False)

    # Should have timestamp suffix
    assert result != existing
    assert result.stem.startswith("document_")
    assert result.suffix == ".md"
    # Should match timestamp pattern: document_YYYYMMDD_HHMMSS.md
    timestamp_part = result.stem.replace("document_", "")
    assert len(timestamp_part) == 15  # YYYYMMDD_HHMMSS


@pytest.mark.unit
def test_overwrite_mode_uses_same_path(temp_dir):
    """Test that overwrite mode uses same path without timestamp."""
    from batch2md.output_manager import resolve_output_path

    input_file = temp_dir / "document.docx"
    output_dir = temp_dir / "markdown"
    base_dir = temp_dir

    # Create existing file
    output_dir.mkdir(parents=True)
    existing = output_dir / "document.md"
    existing.write_text("existing content")

    result = resolve_output_path(input_file, output_dir, base_dir, overwrite=True)

    # Should use same path when overwrite=True
    assert result == existing


@pytest.mark.unit
def test_create_output_directories(temp_dir):
    """Test creating output directories."""
    from batch2md.output_manager import create_output_directories

    output_path = temp_dir / "markdown" / "subdir" / "document.md"
    images_dir = temp_dir / "markdown" / "images"

    assert not output_path.parent.exists()
    assert not images_dir.exists()

    create_output_directories(output_path, images_dir)

    assert output_path.parent.exists()
    assert images_dir.exists()


@pytest.mark.unit
def test_images_directory_creation(temp_dir):
    """Test that images directory is created correctly."""
    from batch2md.output_manager import create_output_directories

    output_path = temp_dir / "markdown" / "doc.md"
    images_dir = temp_dir / "markdown" / "images"

    create_output_directories(output_path, images_dir)

    assert images_dir.exists()
    assert images_dir.is_dir()


@pytest.mark.unit
def test_markdown_directory_structure(temp_dir):
    """Test complete markdown directory structure creation."""
    from batch2md.output_manager import create_output_directories

    output_path = temp_dir / "markdown" / "subdir1" / "subdir2" / "doc.md"
    images_dir = temp_dir / "markdown" / "images"

    create_output_directories(output_path, images_dir)

    # All parent directories should exist
    assert (temp_dir / "markdown").exists()
    assert (temp_dir / "markdown" / "subdir1").exists()
    assert (temp_dir / "markdown" / "subdir1" / "subdir2").exists()
    assert images_dir.exists()


@pytest.mark.unit
def test_output_path_relative_to_base(temp_dir):
    """Test that output path is correctly calculated relative to base."""
    from batch2md.output_manager import resolve_output_path

    # Input file is in subdirectory
    base_dir = temp_dir / "input"
    input_file = base_dir / "project" / "docs" / "readme.docx"
    output_dir = temp_dir / "output"

    result = resolve_output_path(input_file, output_dir, base_dir)

    # Should preserve relative path from base
    expected = output_dir / "project" / "docs" / "readme.md"
    assert result == expected


@pytest.mark.unit
def test_resolve_handles_different_extensions(temp_dir):
    """Test that resolver handles various input extensions."""
    from batch2md.output_manager import resolve_output_path

    output_dir = temp_dir / "markdown"
    base_dir = temp_dir

    test_files = [
        "doc.docx",
        "pres.pptx",
        "sheet.xlsx",
        "file.pdf",
        "text.odt",
    ]

    for filename in test_files:
        input_file = temp_dir / filename
        result = resolve_output_path(input_file, output_dir, base_dir)

        # All should become .md
        assert result.suffix == ".md"
        # Basename should be preserved
        assert result.stem == input_file.stem


@pytest.mark.unit
def test_timestamp_format_is_valid(temp_dir):
    """Test that timestamp format is valid and parseable."""
    from batch2md.output_manager import resolve_output_path

    input_file = temp_dir / "document.docx"
    output_dir = temp_dir / "markdown"
    base_dir = temp_dir

    # Create existing file
    output_dir.mkdir(parents=True)
    (output_dir / "document.md").write_text("existing")

    result = resolve_output_path(input_file, output_dir, base_dir, overwrite=False)

    # Extract timestamp
    timestamp_str = result.stem.replace("document_", "")

    # Should be parseable as datetime
    try:
        dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        assert dt is not None
    except ValueError:
        pytest.fail(f"Invalid timestamp format: {timestamp_str}")


@pytest.mark.unit
def test_multiple_conflicts_get_different_timestamps(temp_dir):
    """Test that multiple conflicts get different timestamps."""
    from batch2md.output_manager import resolve_output_path

    input_file = temp_dir / "document.docx"
    output_dir = temp_dir / "markdown"
    base_dir = temp_dir

    output_dir.mkdir(parents=True)

    # Create first conflict
    result1 = resolve_output_path(input_file, output_dir, base_dir, overwrite=False)
    result1.write_text("first")

    # Small delay to ensure different timestamp
    time.sleep(1)

    # Create second conflict
    result2 = resolve_output_path(input_file, output_dir, base_dir, overwrite=False)

    # Should be different
    assert result1 != result2
    assert result1.stem != result2.stem


@pytest.mark.unit
def test_resolve_with_special_characters_in_filename(temp_dir):
    """Test handling filenames with special characters."""
    from batch2md.output_manager import resolve_output_path

    # Files with spaces and special chars
    input_file = temp_dir / "My Document (Draft) - Final.docx"
    output_dir = temp_dir / "markdown"
    base_dir = temp_dir

    result = resolve_output_path(input_file, output_dir, base_dir)

    # Should preserve the name (spaces and special chars)
    assert result.stem == "My Document (Draft) - Final"
    assert result.suffix == ".md"


@pytest.mark.unit
def test_resolve_with_unicode_filename(temp_dir):
    """Test handling Unicode characters in filenames."""
    from batch2md.output_manager import resolve_output_path

    input_file = temp_dir / "文档测试.docx"
    output_dir = temp_dir / "markdown"
    base_dir = temp_dir

    result = resolve_output_path(input_file, output_dir, base_dir)

    assert result.stem == "文档测试"
    assert result.suffix == ".md"


@pytest.mark.unit
def test_get_images_dir_for_document(temp_dir):
    """Test getting images directory path for a document."""
    from batch2md.output_manager import get_images_dir

    output_path = temp_dir / "markdown" / "document.md"
    images_dir = get_images_dir(output_path)

    # Images directory should be in markdown root
    expected = temp_dir / "markdown" / "images"
    assert images_dir == expected


@pytest.mark.unit
def test_get_relative_image_path(temp_dir):
    """Test getting relative path from markdown to image."""
    from batch2md.output_manager import get_relative_image_path

    md_path = temp_dir / "markdown" / "subdir" / "document.md"
    img_path = temp_dir / "markdown" / "images" / "doc_img1.png"

    relative = get_relative_image_path(md_path, img_path)

    # Should be relative path from md file to image
    # From markdown/subdir/document.md to markdown/images/doc_img1.png
    assert relative == Path("../images/doc_img1.png")


@pytest.mark.unit
def test_create_directories_is_idempotent(temp_dir):
    """Test that creating directories multiple times is safe."""
    from batch2md.output_manager import create_output_directories

    output_path = temp_dir / "markdown" / "doc.md"
    images_dir = temp_dir / "markdown" / "images"

    # Create once
    create_output_directories(output_path, images_dir)
    assert output_path.parent.exists()

    # Create again - should not error
    create_output_directories(output_path, images_dir)
    assert output_path.parent.exists()


@pytest.mark.unit
def test_resolve_path_with_no_extension(temp_dir):
    """Test handling files without extension."""
    from batch2md.output_manager import resolve_output_path

    input_file = temp_dir / "README"
    output_dir = temp_dir / "markdown"
    base_dir = temp_dir

    result = resolve_output_path(input_file, output_dir, base_dir)

    assert result == output_dir / "README.md"
