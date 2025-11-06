"""CLI contract tests for batch2md.

These tests define the command-line interface behavior.
Tests must be written and approved before implementation.
"""

import pytest
import subprocess
import sys
from pathlib import Path


@pytest.mark.unit
def test_cli_module_importable():
    """Test that the CLI module can be imported."""
    try:
        from batch2md import cli
        assert cli is not None
    except ImportError as e:
        pytest.fail(f"Cannot import batch2md.cli: {e}")


@pytest.mark.unit
def test_cli_help_displays():
    """Test that --help displays help message."""
    result = subprocess.run(
        [sys.executable, "-m", "batch2md.main", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "batch2md" in result.stdout.lower() or "usage" in result.stdout.lower()


@pytest.mark.unit
def test_cli_accepts_directory_argument(temp_dir):
    """Test that CLI accepts a directory path as argument."""
    # This will fail until implemented, but defines the contract
    result = subprocess.run(
        [sys.executable, "-m", "batch2md.main", str(temp_dir), "--dry-run"],
        capture_output=True,
        text=True
    )
    # Should not crash on valid directory
    assert result.returncode in [0, 1]  # 0=success, 1=partial failure


@pytest.mark.unit
def test_cli_validates_directory_exists():
    """Test that CLI validates input directory exists."""
    result = subprocess.run(
        [sys.executable, "-m", "batch2md.main", "/nonexistent/directory"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 2  # Error exit code
    assert "not exist" in result.stderr.lower() or "not found" in result.stderr.lower()


@pytest.mark.unit
def test_cli_recursive_flag_default(temp_dir):
    """Test that recursive mode is enabled by default."""
    from batch2md.cli import parse_args

    # Mock sys.argv
    import sys
    old_argv = sys.argv
    try:
        sys.argv = ["batch2md", str(temp_dir)]
        config = parse_args()
        assert config.recursive is True
    finally:
        sys.argv = old_argv


@pytest.mark.unit
def test_cli_no_recursive_flag(temp_dir):
    """Test --no-recursive flag disables recursive scanning."""
    from batch2md.cli import parse_args

    import sys
    old_argv = sys.argv
    try:
        sys.argv = ["batch2md", str(temp_dir), "--no-recursive"]
        config = parse_args()
        assert config.recursive is False
    finally:
        sys.argv = old_argv


@pytest.mark.unit
def test_cli_output_directory_option(temp_dir):
    """Test --output option sets custom output directory."""
    from batch2md.cli import parse_args

    output_dir = temp_dir / "custom_output"

    import sys
    old_argv = sys.argv
    try:
        sys.argv = ["batch2md", str(temp_dir), "--output", str(output_dir)]
        config = parse_args()
        assert config.output_dir == output_dir
    finally:
        sys.argv = old_argv


@pytest.mark.unit
def test_cli_verbose_flag(temp_dir):
    """Test --verbose flag enables verbose mode."""
    from batch2md.cli import parse_args

    import sys
    old_argv = sys.argv
    try:
        sys.argv = ["batch2md", str(temp_dir), "--verbose"]
        config = parse_args()
        assert config.verbose is True
    finally:
        sys.argv = old_argv


@pytest.mark.unit
def test_cli_dry_run_flag(temp_dir):
    """Test --dry-run flag enables dry run mode."""
    from batch2md.cli import parse_args

    import sys
    old_argv = sys.argv
    try:
        sys.argv = ["batch2md", str(temp_dir), "--dry-run"]
        config = parse_args()
        assert config.dry_run is True
    finally:
        sys.argv = old_argv


@pytest.mark.unit
def test_cli_backend_option(temp_dir):
    """Test --backend option sets MinerU backend."""
    from batch2md.cli import parse_args

    import sys
    old_argv = sys.argv
    try:
        sys.argv = ["batch2md", str(temp_dir), "--backend", "vlm"]
        config = parse_args()
        assert config.mineru_backend == "vlm"
    finally:
        sys.argv = old_argv


@pytest.mark.unit
def test_cli_json_output_flag(temp_dir):
    """Test --json flag enables JSON output."""
    from batch2md.cli import parse_args

    import sys
    old_argv = sys.argv
    try:
        sys.argv = ["batch2md", str(temp_dir), "--json"]
        config = parse_args()
        assert config.json_output is True
    finally:
        sys.argv = old_argv


@pytest.mark.integration
def test_cli_exit_code_success(temp_dir, sample_text_file):
    """Test CLI returns exit code 0 on success."""
    # Create a simple test case that should succeed
    result = subprocess.run(
        [sys.executable, "-m", "batch2md.main", str(temp_dir), "--dry-run"],
        capture_output=True,
        text=True
    )
    # Dry run should succeed with exit code 0
    assert result.returncode == 0


@pytest.mark.integration
def test_cli_exit_code_total_failure(temp_dir):
    """Test CLI returns exit code 2 on critical error."""
    # Test with invalid input (not a directory)
    invalid_path = temp_dir / "nonexistent"
    result = subprocess.run(
        [sys.executable, "-m", "batch2md.main", str(invalid_path)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 2


@pytest.mark.unit
def test_config_get_output_dir_default(temp_dir):
    """Test that default output directory is input_dir/markdown."""
    from batch2md.models import ConversionConfig

    config = ConversionConfig(input_dir=temp_dir)
    expected = temp_dir / "markdown"
    assert config.get_output_dir() == expected


@pytest.mark.unit
def test_config_get_output_dir_custom(temp_dir):
    """Test that custom output directory is used when specified."""
    from batch2md.models import ConversionConfig

    custom_output = temp_dir / "custom"
    config = ConversionConfig(input_dir=temp_dir, output_dir=custom_output)
    assert config.get_output_dir() == custom_output
