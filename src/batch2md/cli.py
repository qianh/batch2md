"""CLI interface for batch2md."""

import argparse
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import List

from .models import (
    ConversionConfig,
    ConversionJob,
    ConversionSummary,
    ConversionStatus,
    SupportedFormat
)
from .scanner import scan_documents
from .converters import convert_to_pdf, convert_to_markdown, extract_images
from .output_manager import (
    resolve_output_path,
    create_output_directories,
    get_images_dir
)


def parse_args() -> ConversionConfig:
    """
    Parse command-line arguments.

    Returns:
        ConversionConfig with parsed settings
    """
    parser = argparse.ArgumentParser(
        prog="batch2md",
        description="Batch convert documents to Markdown via PDF using MinerU"
    )

    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing documents to convert"
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        dest="output_dir",
        help="Output directory (default: INPUT_DIR/markdown/)"
    )

    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Process only top-level files, skip subdirectories"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress information"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be converted without converting"
    )

    parser.add_argument(
        "--backend",
        choices=["pipeline", "vlm", "vllm"],
        default="pipeline",
        help="MinerU backend (default: pipeline)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON"
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files instead of adding timestamp"
    )

    args = parser.parse_args()

    # Validate input directory
    if not args.input_dir.exists():
        print(f"Error: Input directory not found: {args.input_dir}", file=sys.stderr)
        sys.exit(2)

    if not args.input_dir.is_dir():
        print(f"Error: Input path is not a directory: {args.input_dir}", file=sys.stderr)
        sys.exit(2)

    # Create config
    config = ConversionConfig(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        recursive=not args.no_recursive,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        mineru_backend=args.backend,
        verbose=args.verbose,
        json_output=args.json_output
    )

    return config


def format_progress(current: int, total: int, filename: str, status: str = "") -> str:
    """
    Format progress message.

    Args:
        current: Current file number
        total: Total number of files
        filename: Name of current file
        status: Status message

    Returns:
        Formatted progress string
    """
    progress = f"Processing [{current}/{total}]: {filename}"
    if status:
        progress += f" - {status}"
    return progress


def run_conversion(config: ConversionConfig) -> ConversionSummary:
    """
    Main conversion logic.

    Args:
        config: Conversion configuration

    Returns:
        ConversionSummary with results
    """
    start_time = datetime.now()

    # Get output directory first to exclude it from scanning
    output_dir = config.get_output_dir()

    # Scan for documents, excluding output and temp directories
    exclude_dirs = [output_dir]

    if config.verbose:
        print(f"Scanning directory: {config.input_dir}")
        print(f"Excluding output directory: {output_dir}")

    documents = scan_documents(config.input_dir, config.recursive, exclude_dirs)

    if config.verbose:
        print(f"Found {len(documents)} document(s)")

    if len(documents) == 0:
        print("No supported documents found")
        return ConversionSummary(
            total_files=0,
            successful=0,
            failed=0,
            skipped=0,
            failed_jobs=[],
            completed_jobs=[],
            start_time=start_time,
            end_time=datetime.now()
        )

    # output_dir was already retrieved above for exclusion

    if config.dry_run:
        if config.verbose:
            print(f"\nDry run mode - no files will be converted")
            print(f"Output would go to: {output_dir}\n")

        # Show what would be processed
        for i, doc in enumerate(documents, 1):
            print(format_progress(i, len(documents), doc.name, "would be converted"))

        return ConversionSummary(
            total_files=len(documents),
            successful=0,
            failed=0,
            skipped=len(documents),
            failed_jobs=[],
            completed_jobs=[],
            start_time=start_time,
            end_time=datetime.now()
        )

    # Process each document
    completed_jobs: List[ConversionJob] = []
    failed_jobs: List[ConversionJob] = []

    for i, doc_path in enumerate(documents, 1):
        # Create conversion job
        output_path = resolve_output_path(
            doc_path,
            output_dir,
            config.input_dir,
            config.overwrite
        )
        images_dir = get_images_dir(output_path)

        # Get input file size
        input_size = doc_path.stat().st_size if doc_path.exists() else 0

        job = ConversionJob(
            input_path=doc_path,
            pdf_path=None,
            output_path=output_path,
            images_dir=images_dir,
            status=ConversionStatus.PENDING,
            start_time=datetime.now(),
            file_size_bytes=input_size
        )

        try:
            # Show progress
            print(format_progress(i, len(documents), doc_path.name))

            # Create output directories
            create_output_directories(output_path, images_dir)

            # Step 1: Convert to PDF if needed
            if SupportedFormat.requires_pdf_conversion(doc_path):
                if config.verbose:
                    print(f"  → Converting to PDF...")

                job.status = ConversionStatus.CONVERTING_TO_PDF
                pdf_path = convert_to_pdf(doc_path, output_dir / "temp_pdfs")
                job.pdf_path = pdf_path
            else:
                # Already a PDF
                job.pdf_path = doc_path

            # Step 2: Convert PDF to Markdown
            if config.verbose:
                print(f"  → Extracting Markdown...")

            job.status = ConversionStatus.CONVERTING_TO_MD
            md_path, mineru_temp_dir = convert_to_markdown(
                job.pdf_path,
                output_path,  # Pass full path with potential timestamp suffix
                config.mineru_backend
            )

            # Step 3: Extract images and update references
            if config.verbose:
                print(f"  → Extracting images...")

            images = extract_images(
                md_path,
                mineru_temp_dir,
                images_dir,
                job.pdf_path.stem
            )
            if config.verbose and len(images) > 0:
                print(f"  → Extracted {len(images)} image(s)")

            # Step 4: Cleanup temporary files
            if config.verbose:
                print(f"  → Cleaning up temporary files...")

            # Clean up MinerU temp directory
            try:
                shutil.rmtree(mineru_temp_dir)
            except Exception as e:
                if config.verbose:
                    print(f"  ⚠ Warning: Could not remove MinerU temp directory: {e}")

            # Clean up temporary PDF if it was converted from another format
            if SupportedFormat.requires_pdf_conversion(doc_path) and job.pdf_path and job.pdf_path.exists():
                try:
                    job.pdf_path.unlink()
                    # Also try to remove temp_pdfs directory if empty
                    temp_pdfs_dir = job.pdf_path.parent
                    if temp_pdfs_dir.name == "temp_pdfs" and not any(temp_pdfs_dir.iterdir()):
                        temp_pdfs_dir.rmdir()
                except Exception as e:
                    if config.verbose:
                        print(f"  ⚠ Warning: Could not remove temporary PDF: {e}")

            # Get output file size
            job.output_size_bytes = md_path.stat().st_size if md_path.exists() else 0

            # Success
            job.status = ConversionStatus.COMPLETED
            job.end_time = datetime.now()
            completed_jobs.append(job)

            if config.verbose:
                print(f"  ✓ Completed successfully")

        except Exception as e:
            # Failure
            job.status = ConversionStatus.FAILED
            job.error = str(e)
            job.end_time = datetime.now()
            failed_jobs.append(job)

            print(f"  ✗ Failed: {e}")

            if config.verbose:
                import traceback
                traceback.print_exc()

    # Create summary
    end_time = datetime.now()
    summary = ConversionSummary(
        total_files=len(documents),
        successful=len(completed_jobs),
        failed=len(failed_jobs),
        skipped=0,
        failed_jobs=failed_jobs,
        completed_jobs=completed_jobs,
        start_time=start_time,
        end_time=end_time
    )

    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary: {summary.successful}/{summary.total_files} files converted successfully")
    if summary.failed > 0:
        print(f"  {summary.failed} failed")
    print(f"Elapsed time: {summary.elapsed_time:.1f}s")
    print(f"{'='*60}")

    # JSON output if requested
    if config.json_output:
        import json
        print(json.dumps(summary.to_dict(), indent=2))

    return summary
