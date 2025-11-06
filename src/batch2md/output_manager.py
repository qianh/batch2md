"""Output path management and file organization."""

from pathlib import Path
from datetime import datetime


def resolve_output_path(
    input_path: Path,
    output_dir: Path,
    base_dir: Path,
    overwrite: bool = False
) -> Path:
    """
    Resolve output path with subdirectory mirroring and conflict handling.

    Args:
        input_path: Original input file path
        output_dir: Base output directory
        base_dir: Base directory for calculating relative paths
        overwrite: If False, add timestamp suffix for conflicts

    Returns:
        Resolved output path for Markdown file
    """
    # Get relative path from base directory
    try:
        rel_path = input_path.relative_to(base_dir)
    except ValueError:
        # If input_path is not relative to base_dir, use filename only
        rel_path = Path(input_path.name)

    # Change extension to .md
    md_filename = rel_path.stem + ".md"
    output_path = output_dir / rel_path.parent / md_filename

    # Handle file conflicts
    if output_path.exists() and not overwrite:
        # Add timestamp suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_filename = f"{rel_path.stem}_{timestamp}.md"
        output_path = output_dir / rel_path.parent / md_filename

    return output_path


def create_output_directories(output_path: Path, images_dir: Path) -> None:
    """
    Create necessary output directories.

    Args:
        output_path: Path where Markdown file will be saved
        images_dir: Directory for images
    """
    # Create parent directory for markdown file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create images directory
    images_dir.mkdir(parents=True, exist_ok=True)


def get_images_dir(output_path: Path) -> Path:
    """
    Get images directory path for a document.

    Args:
        output_path: Path to Markdown file

    Returns:
        Path to images directory (in markdown root)
    """
    # Find the 'markdown' directory in the path
    parts = output_path.parts
    if "markdown" in parts:
        # Get path up to markdown directory
        markdown_idx = parts.index("markdown")
        markdown_root = Path(*parts[:markdown_idx + 1])
        return markdown_root / "images"
    else:
        # Fallback: use parent directory
        return output_path.parent / "images"


def get_relative_image_path(md_path: Path, img_path: Path) -> Path:
    """
    Get relative path from markdown file to image.

    Args:
        md_path: Path to Markdown file
        img_path: Path to image file

    Returns:
        Relative path from MD to image
    """
    try:
        # Calculate relative path
        return Path("..") / img_path.relative_to(md_path.parent.parent)
    except ValueError:
        # If calculation fails, return image name only
        return Path("images") / img_path.name
