"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup after test
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file for testing."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("This is a test document.\nSecond line.\n")
    return file_path


@pytest.fixture
def nested_structure(temp_dir):
    """Create a nested directory structure with test files."""
    # Create directories
    (temp_dir / "subdir1").mkdir()
    (temp_dir / "subdir2").mkdir()

    # Create files
    (temp_dir / "file1.txt").write_text("File 1 content")
    (temp_dir / "subdir1" / "file2.txt").write_text("File 2 content")
    (temp_dir / "subdir2" / "file3.txt").write_text("File 3 content")

    return temp_dir
