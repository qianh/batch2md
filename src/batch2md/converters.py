"""Document conversion functions."""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def check_libreoffice() -> bool:
    """
    Check if LibreOffice is installed and accessible.

    Returns:
        True if LibreOffice is available

    Raises:
        RuntimeError: If LibreOffice is not found
    """
    if shutil.which("soffice") is None:
        raise RuntimeError(
            "LibreOffice not found. Please install LibreOffice:\n"
            "  macOS: brew install libreoffice\n"
            "  Ubuntu: sudo apt-get install libreoffice"
        )
    return True


def check_mineru() -> bool:
    """
    Check if MinerU is installed.

    Returns:
        True if MinerU is available

    Raises:
        ImportError: If MinerU is not installed
    """
    try:
        import mineru
        return True
    except ImportError:
        raise ImportError(
            "MinerU not installed. Please install with:\n"
            "  pip install mineru\n"
            "  mineru download  # Download models"
        )


def convert_to_pdf(doc_path: Path, output_dir: Path) -> Path:
    """
    Convert document to PDF using LibreOffice.

    Args:
        doc_path: Path to document to convert
        output_dir: Directory to save PDF

    Returns:
        Path to generated PDF file

    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If conversion fails
    """
    # Check that input exists
    if not doc_path.exists():
        raise FileNotFoundError(f"Input file not found: {doc_path}")

    # Check LibreOffice availability
    check_libreoffice()

    # Create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # Expected output path
    pdf_path = output_dir / f"{doc_path.stem}.pdf"

    # Run LibreOffice conversion
    try:
        result = subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(output_dir),
                str(doc_path)
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"LibreOffice conversion failed for {doc_path.name}: {e.stderr}"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"LibreOffice conversion timed out for {doc_path.name}"
        )

    # Verify output was created
    if not pdf_path.exists():
        raise RuntimeError(
            f"PDF output not created for {doc_path.name}"
        )

    # Verify PDF is valid (check size and magic bytes)
    if pdf_path.stat().st_size < 100:
        raise RuntimeError(
            f"PDF output is too small for {doc_path.name}"
        )

    # Check PDF magic bytes
    with open(pdf_path, "rb") as f:
        header = f.read(4)
        if header != b"%PDF":
            raise RuntimeError(
                f"Invalid PDF output for {doc_path.name}"
            )

    return pdf_path


def _map_backend(backend: str) -> str:
    """Map legacy backend names to MinerU's current CLI values."""

    backend_map: Dict[str, str] = {
        "pipeline": "pipeline",
        "vlm": "vlm-transformers",
        "vlm-transformers": "vlm-transformers",
        "vllm": "vlm-vllm-engine",
        "vlm-vllm-engine": "vlm-vllm-engine",
        "vlm-http-client": "vlm-http-client",
    }
    return backend_map.get(backend, backend)


def _ensure_backend_dependencies(mapped_backend: str) -> None:
    """Ensure optional dependencies required by a backend are present."""

    if mapped_backend in {"pipeline", "vlm-transformers", "vlm-vllm-engine"}:
        try:
            import torch  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "MinerU backend '{backend}' requires PyTorch. Install it first, e.g.\n"
                "  pip install torch --index-url https://download.pytorch.org/whl/cpu\n"
                "or switch to a different MinerU backend via --backend"
            .format(backend=mapped_backend)) from exc


def convert_to_markdown(
    pdf_path: Path,
    output_md_path: Path,
    backend: str = "pipeline",
    timeout: int = 300
) -> Tuple[Path, Path]:
    """
    Convert PDF to Markdown using MinerU.

    Args:
        pdf_path: Path to PDF file
        output_md_path: Full path where Markdown file should be saved
        backend: MinerU backend to use (pipeline, vlm, or vllm)
        timeout: Seconds to wait for MinerU before aborting

    Returns:
        Tuple of (markdown_file_path, mineru_temp_directory)

    Raises:
        FileNotFoundError: If input PDF doesn't exist
        RuntimeError: If conversion fails
    """
    # Check that input exists
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Check MinerU availability
    check_mineru()

    # Create output directory
    output_dir = output_md_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create a temporary directory for MinerU output
    # MinerU creates complex subdirectory structures, we'll search for the MD later
    temp_output_dir = output_dir / f".mineru_temp_{pdf_path.stem}"
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Run MinerU conversion to temporary directory
        mapped_backend = _map_backend(backend)
        _ensure_backend_dependencies(mapped_backend)
        env = os.environ.copy()
        env.setdefault("MINERU_DEVICE_MODE", "cpu")

        result = subprocess.run(
            [
                "mineru",
                "-p",
                str(pdf_path),
                "-o",
                str(temp_output_dir),
                "--backend",
                mapped_backend,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True,
            env=env,
        )

        # MinerU creates output in a subdirectory structure
        # Look for the markdown file in the temp output
        possible_paths = [
            temp_output_dir / f"{pdf_path.stem}.md",
            temp_output_dir / pdf_path.stem / "auto" / f"{pdf_path.stem}.md",
            temp_output_dir / "auto" / f"{pdf_path.stem}.md",
        ]

        # Find the generated markdown file
        found_md = None
        for possible_path in possible_paths:
            if possible_path.exists():
                found_md = possible_path
                break

        # If not found in expected locations, search
        if not found_md:
            md_files = list(temp_output_dir.rglob("*.md"))
            if md_files:
                found_md = md_files[0]

        if not found_md:
            details = []
            if result.stdout:
                details.append(result.stdout.strip())
            if result.stderr:
                details.append(result.stderr.strip())
            detail_msg = "\n".join([d for d in details if d])
            raise RuntimeError(
                "Markdown output not created for {name}{extra}".format(
                    name=pdf_path.name,
                    extra=f"\nMinerU output:\n{detail_msg}" if detail_msg else ""
                )
            )

        # Move to the requested output path (respecting timestamp suffix if present)
        shutil.move(str(found_md), str(output_md_path))

        # Return both the md path and temp dir path for image extraction
        return (output_md_path, temp_output_dir)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"MinerU conversion failed for {pdf_path.name}: {e.stderr}"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"MinerU conversion timed out for {pdf_path.name}"
        )


def extract_images(
    md_path: Path,
    mineru_temp_dir: Path,
    images_dir: Path,
    pdf_stem: str
) -> List[Path]:
    """
    Extract images from MinerU output and update Markdown references.

    Args:
        md_path: Path to the Markdown file
        mineru_temp_dir: MinerU temporary output directory to search for images
        images_dir: Directory to save images
        pdf_stem: Stem of the PDF file for naming images

    Returns:
        List of paths to extracted images

    Note:
        MinerU extracts images during conversion.
        This function finds them, copies to centralized location, and updates MD references.
    """
    # Create images directory
    images_dir.mkdir(parents=True, exist_ok=True)

    # MinerU extracts images to subdirectories
    # Look for image files
    extracted_images = []
    image_mapping = {}  # Maps old path to new path for reference updating

    # Common image extensions
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']

    # Search for images only in MinerU temp directory (not the entire parent)
    for ext in image_extensions:
        for img_path in mineru_temp_dir.rglob(f"*{ext}"):
            if img_path.is_file():
                # Generate meaningful name
                new_name = f"{pdf_stem}_img{len(extracted_images) + 1}{img_path.suffix}"
                new_path = images_dir / new_name

                # Copy image to centralized directory
                if img_path != new_path:
                    shutil.copy(str(img_path), str(new_path))

                # Track old -> new mapping for reference updating
                # Store the relative path from mineru_temp_dir to help match in MD
                try:
                    rel_old_path = img_path.relative_to(mineru_temp_dir)
                    image_mapping[str(rel_old_path)] = new_name
                    image_mapping[img_path.name] = new_name  # Also map by filename
                except ValueError:
                    pass

                extracted_images.append(new_path)

    # Update Markdown file references if we found images
    if extracted_images and md_path.exists():
        try:
            # Read markdown content
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Update image references
            # Common patterns: ![alt](path), <img src="path">
            import re

            # Calculate relative path from MD to images directory
            try:
                rel_images_dir = images_dir.relative_to(md_path.parent)
            except ValueError:
                # If can't calculate relative path, use absolute
                rel_images_dir = images_dir

            # Replace image references
            modified = False
            for old_ref, new_name in image_mapping.items():
                # Pattern 1: Markdown syntax ![...](...old_ref...)
                pattern1 = re.compile(
                    r'!\[([^\]]*)\]\(([^)]*' + re.escape(old_ref) + r'[^)]*)\)',
                    re.IGNORECASE
                )
                new_ref1 = f'![\\1]({rel_images_dir}/{new_name})'
                if pattern1.search(md_content):
                    md_content = pattern1.sub(new_ref1, md_content)
                    modified = True

                # Pattern 2: HTML img tag src="...old_ref..."
                pattern2 = re.compile(
                    r'<img([^>]*)src=["\']([^"\']*' + re.escape(old_ref) + r'[^"\']*)["\']([^>]*)>',
                    re.IGNORECASE
                )
                new_ref2 = f'<img\\1src="{rel_images_dir}/{new_name}"\\3>'
                if pattern2.search(md_content):
                    md_content = pattern2.sub(new_ref2, md_content)
                    modified = True

            # Write back if modified
            if modified:
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)

        except Exception as e:
            # Don't fail the whole conversion if image reference updating fails
            import warnings
            warnings.warn(f"Failed to update image references in {md_path}: {e}")

    return extracted_images
