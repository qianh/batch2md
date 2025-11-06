#!/usr/bin/env python
"""Script to create test fixtures for batch2md testing."""

import subprocess
import sys
from pathlib import Path


def check_libreoffice():
    """Check if LibreOffice is installed."""
    try:
        result = subprocess.run(
            ["soffice", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"✓ LibreOffice found: {result.stdout.strip()}")
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ LibreOffice not found. Please install LibreOffice first.")
        print("\n  macOS: brew install libreoffice")
        print("  Ubuntu: sudo apt-get install libreoffice")
        return False


def create_text_files(fixtures_dir: Path):
    """Create simple text files for testing."""
    print("\nCreating text files...")

    # Simple document
    simple_txt = fixtures_dir / "simple.txt"
    simple_txt.write_text(
        "# Test Document\n\n"
        "This is a simple test document.\n\n"
        "It contains multiple paragraphs.\n\n"
        "And this is the third paragraph.\n"
    )
    print(f"  ✓ Created {simple_txt.name}")

    # Document with table-like structure
    table_txt = fixtures_dir / "with_table.txt"
    table_txt.write_text(
        "# Document with Table\n\n"
        "Name\tAge\tCity\n"
        "Alice\t30\tNew York\n"
        "Bob\t25\tLos Angeles\n"
        "Charlie\t35\tChicago\n"
    )
    print(f"  ✓ Created {table_txt.name}")

    # Nested document
    nested_dir = fixtures_dir / "nested"
    nested_dir.mkdir(exist_ok=True)
    nested_txt = nested_dir / "nested_sample.txt"
    nested_txt.write_text(
        "# Nested Test Document\n\n"
        "This document is in a subdirectory.\n"
    )
    print(f"  ✓ Created nested/{nested_txt.name}")


def convert_to_office_formats(fixtures_dir: Path):
    """Convert text files to Office formats using LibreOffice."""
    print("\nConverting to Office formats...")

    txt_files = list(fixtures_dir.glob("*.txt"))

    for txt_file in txt_files:
        # Convert to DOCX
        try:
            subprocess.run(
                [
                    "soffice",
                    "--headless",
                    "--convert-to", "docx",
                    "--outdir", str(fixtures_dir),
                    str(txt_file)
                ],
                capture_output=True,
                timeout=30,
                check=True
            )
            print(f"  ✓ Converted {txt_file.name} to DOCX")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to convert {txt_file.name}: {e}")
        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout converting {txt_file.name}")

    # Convert nested file
    nested_txt = fixtures_dir / "nested" / "nested_sample.txt"
    if nested_txt.exists():
        try:
            subprocess.run(
                [
                    "soffice",
                    "--headless",
                    "--convert-to", "docx",
                    "--outdir", str(fixtures_dir / "nested"),
                    str(nested_txt)
                ],
                capture_output=True,
                timeout=30,
                check=True
            )
            print(f"  ✓ Converted nested/{nested_txt.name} to DOCX")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print(f"  ✗ Failed to convert nested/{nested_txt.name}")


def create_corrupted_file(fixtures_dir: Path):
    """Create a corrupted DOCX file for error testing."""
    print("\nCreating corrupted file for error testing...")

    corrupted = fixtures_dir / "corrupted.docx"
    # Write invalid ZIP data (DOCX is a ZIP file)
    corrupted.write_bytes(b"This is not a valid DOCX file content")
    print(f"  ✓ Created {corrupted.name}")


def create_pdf_sample(fixtures_dir: Path):
    """Create a sample PDF file."""
    print("\nCreating sample PDF...")

    # Check if we have a DOCX to convert
    docx_files = list(fixtures_dir.glob("*.docx"))
    if docx_files and docx_files[0].name != "corrupted.docx":
        try:
            subprocess.run(
                [
                    "soffice",
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", str(fixtures_dir),
                    str(docx_files[0])
                ],
                capture_output=True,
                timeout=30,
                check=True
            )
            print(f"  ✓ Created sample.pdf from {docx_files[0].name}")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print(f"  ✗ Failed to create PDF")
    else:
        print("  ⚠ No valid DOCX file found to create PDF")


def main():
    """Main function to create all test fixtures."""
    print("=" * 60)
    print("batch2md Test Fixtures Setup")
    print("=" * 60)

    # Get fixtures directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    fixtures_dir = project_dir / "tests" / "fixtures"

    print(f"\nFixtures directory: {fixtures_dir}")

    # Check prerequisites
    if not check_libreoffice():
        sys.exit(1)

    # Create fixtures directory
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    # Create test files
    create_text_files(fixtures_dir)
    convert_to_office_formats(fixtures_dir)
    create_corrupted_file(fixtures_dir)
    create_pdf_sample(fixtures_dir)

    # Summary
    print("\n" + "=" * 60)
    print("✓ Test fixtures created successfully!")
    print("=" * 60)
    print(f"\nCreated files:")
    for file in sorted(fixtures_dir.rglob("*")):
        if file.is_file():
            print(f"  - {file.relative_to(fixtures_dir)}")

    print("\n" + "=" * 60)
    print("You can now run tests with: pytest tests/ -v")
    print("=" * 60)


if __name__ == "__main__":
    main()
