"""Document scanner for discovering files to convert."""

from pathlib import Path
from typing import List, Optional
from .models import SupportedFormat


def scan_documents(
    path: Path,
    recursive: bool = True,
    exclude_dirs: Optional[List[Path]] = None
) -> List[Path]:
    """
    Scan directory for supported document files.

    Args:
        path: Directory to scan
        recursive: If True, scan subdirectories recursively
        exclude_dirs: List of directories to exclude from scanning

    Returns:
        Sorted list of paths to supported documents
    """
    documents = []
    exclude_dirs = exclude_dirs or []

    # Normalize exclude paths to absolute paths for comparison
    exclude_paths = set()
    for exclude_dir in exclude_dirs:
        try:
            # Resolve to absolute path
            abs_exclude = exclude_dir.resolve()
            exclude_paths.add(abs_exclude)
        except (ValueError, OSError):
            # Skip invalid paths
            continue

    if recursive:
        # Recursively find all files
        pattern = "**/*"
    else:
        # Only top-level files
        pattern = "*"

    # Find all files matching pattern
    for file_path in path.glob(pattern):
        # Skip directories
        if not file_path.is_file():
            continue

        # Skip hidden files (starting with .)
        if file_path.name.startswith('.'):
            continue

        # Check if file is under any excluded directory
        try:
            file_abs = file_path.resolve()
            is_excluded = False
            for exclude_path in exclude_paths:
                try:
                    # Check if file is under this excluded directory
                    file_abs.relative_to(exclude_path)
                    is_excluded = True
                    break
                except ValueError:
                    # Not under this excluded path
                    continue

            if is_excluded:
                continue

        except (ValueError, OSError):
            # Skip files we can't resolve
            continue

        # Check if file format is supported
        if SupportedFormat.is_supported(file_path):
            documents.append(file_path)

    # Return sorted list
    return sorted(documents)
