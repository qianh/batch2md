"""Tests for document scanner module.

Tests document discovery and filtering functionality.
"""

import pytest
from pathlib import Path


@pytest.mark.unit
def test_scan_finds_docx_files(temp_dir):
    """Test that scanner finds DOCX files."""
    from batch2md.scanner import scan_documents

    # Create test files
    (temp_dir / "test1.docx").touch()
    (temp_dir / "test2.docx").touch()
    (temp_dir / "test.txt").touch()

    results = scan_documents(temp_dir, recursive=False)

    assert len(results) == 2
    assert all(f.suffix == ".docx" for f in results)


@pytest.mark.unit
def test_scan_finds_multiple_formats(temp_dir):
    """Test that scanner finds various document formats."""
    from batch2md.scanner import scan_documents

    # Create test files
    (temp_dir / "doc.docx").touch()
    (temp_dir / "pres.pptx").touch()
    (temp_dir / "sheet.xlsx").touch()
    (temp_dir / "file.pdf").touch()
    (temp_dir / "text.txt").touch()  # Should be ignored

    results = scan_documents(temp_dir, recursive=False)

    # Should find DOCX, PPTX, XLSX, PDF (not TXT)
    assert len(results) == 4
    extensions = {f.suffix for f in results}
    assert extensions == {".docx", ".pptx", ".xlsx", ".pdf"}


@pytest.mark.unit
def test_scan_recursive_subdirectories(nested_structure):
    """Test recursive directory scanning."""
    from batch2md.scanner import scan_documents

    # nested_structure has files in root, subdir1, and subdir2
    # But they're .txt files, let's create .docx files
    (nested_structure / "root.docx").touch()
    (nested_structure / "subdir1" / "sub1.docx").touch()
    (nested_structure / "subdir2" / "sub2.docx").touch()

    results = scan_documents(nested_structure, recursive=True)

    assert len(results) == 3
    # Verify files from different levels
    names = {f.name for f in results}
    assert names == {"root.docx", "sub1.docx", "sub2.docx"}


@pytest.mark.unit
def test_scan_non_recursive_top_level_only(nested_structure):
    """Test non-recursive mode (top-level only)."""
    from batch2md.scanner import scan_documents

    (nested_structure / "root.docx").touch()
    (nested_structure / "subdir1" / "sub1.docx").touch()
    (nested_structure / "subdir2" / "sub2.docx").touch()

    results = scan_documents(nested_structure, recursive=False)

    assert len(results) == 1
    assert results[0].name == "root.docx"


@pytest.mark.unit
def test_scan_ignores_unsupported_formats(temp_dir):
    """Test that unsupported formats are ignored."""
    from batch2md.scanner import scan_documents

    # Create unsupported files
    (temp_dir / "image.png").touch()
    (temp_dir / "video.mp4").touch()
    (temp_dir / "archive.zip").touch()
    (temp_dir / "supported.docx").touch()

    results = scan_documents(temp_dir, recursive=False)

    assert len(results) == 1
    assert results[0].name == "supported.docx"


@pytest.mark.unit
def test_scan_empty_directory_returns_empty_list(temp_dir):
    """Test scanning empty directory returns empty list."""
    from batch2md.scanner import scan_documents

    results = scan_documents(temp_dir, recursive=True)

    assert results == []


@pytest.mark.unit
def test_scan_filters_by_supported_formats(temp_dir):
    """Test that scanner uses SupportedFormat enum for filtering."""
    from batch2md.scanner import scan_documents
    from batch2md.models import SupportedFormat

    # Create files for all supported formats
    for fmt in SupportedFormat:
        (temp_dir / f"test{fmt.value}").touch()

    results = scan_documents(temp_dir, recursive=False)

    # Should find all supported format files
    assert len(results) == len(SupportedFormat)
    found_extensions = {f.suffix for f in results}
    expected_extensions = {fmt.value for fmt in SupportedFormat}
    assert found_extensions == expected_extensions


@pytest.mark.unit
def test_scan_returns_sorted_paths(temp_dir):
    """Test that scan results are sorted."""
    from batch2md.scanner import scan_documents

    # Create files in non-alphabetical order
    (temp_dir / "zebra.docx").touch()
    (temp_dir / "apple.docx").touch()
    (temp_dir / "banana.docx").touch()

    results = scan_documents(temp_dir, recursive=False)

    # Results should be sorted
    names = [f.name for f in results]
    assert names == sorted(names)


@pytest.mark.unit
def test_scan_handles_hidden_files(temp_dir):
    """Test that hidden files (starting with .) are ignored."""
    from batch2md.scanner import scan_documents

    (temp_dir / "visible.docx").touch()
    (temp_dir / ".hidden.docx").touch()

    results = scan_documents(temp_dir, recursive=False)

    # Should not include hidden files
    assert len(results) == 1
    assert results[0].name == "visible.docx"


@pytest.mark.unit
def test_scan_handles_case_insensitive_extensions(temp_dir):
    """Test that extensions are matched case-insensitively."""
    from batch2md.scanner import scan_documents

    # Create files with various case extensions
    (temp_dir / "file1.DOCX").touch()
    (temp_dir / "file2.DocX").touch()
    (temp_dir / "file3.docx").touch()

    results = scan_documents(temp_dir, recursive=False)

    # All should be found regardless of case
    assert len(results) == 3
