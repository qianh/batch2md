"""Data models for batch2md."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ConversionStatus(Enum):
    """Status of a conversion job."""
    PENDING = "pending"
    CONVERTING_TO_PDF = "converting_to_pdf"
    CONVERTING_TO_MD = "converting_to_md"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ConversionJob:
    """Represents a single document conversion operation."""

    # File paths
    input_path: Path
    pdf_path: Optional[Path]
    output_path: Path
    images_dir: Path

    # Status tracking
    status: ConversionStatus
    error: Optional[str] = None

    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    # Metadata
    file_size_bytes: int = 0
    output_size_bytes: int = 0

    @property
    def elapsed_time(self) -> float:
        """Return elapsed time in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def is_completed(self) -> bool:
        """Check if job is completed."""
        return self.status == ConversionStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if job failed."""
        return self.status == ConversionStatus.FAILED


@dataclass
class ConversionSummary:
    """Summary of a batch conversion operation."""

    # Counts
    total_files: int
    successful: int
    failed: int
    skipped: int

    # Details
    failed_jobs: List[ConversionJob]
    completed_jobs: List[ConversionJob]

    # Timing
    start_time: datetime
    end_time: datetime

    @property
    def elapsed_time(self) -> float:
        """Total elapsed time in seconds."""
        return (self.end_time - self.start_time).total_seconds()

    @property
    def success_rate(self) -> float:
        """Success rate as percentage (0-100)."""
        if self.total_files == 0:
            return 0.0
        return (self.successful / self.total_files) * 100

    @property
    def exit_code(self) -> int:
        """Exit code for CLI: 0 = success, 1 = partial failure, 2 = total failure."""
        if self.failed == 0:
            return 0  # All successful
        elif self.successful > 0:
            return 1  # Some succeeded, some failed
        else:
            return 2  # All failed

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "summary": {
                "total_files": self.total_files,
                "successful": self.successful,
                "failed": self.failed,
                "skipped": self.skipped,
                "success_rate": f"{self.success_rate:.1f}%",
                "elapsed_time": self.elapsed_time
            },
            "failures": [
                {
                    "input_path": str(job.input_path),
                    "error": job.error
                }
                for job in self.failed_jobs
            ]
        }


@dataclass
class ConversionConfig:
    """Configuration for batch conversion."""

    # Paths
    input_dir: Path
    output_dir: Optional[Path] = None

    # Behavior
    recursive: bool = True
    overwrite: bool = False
    dry_run: bool = False

    # MinerU settings
    mineru_backend: str = "pipeline"

    # Output
    verbose: bool = False
    json_output: bool = False

    # Performance
    max_workers: int = 1

    def get_output_dir(self) -> Path:
        """Get the actual output directory."""
        if self.output_dir:
            return self.output_dir
        return self.input_dir / "markdown"


class SupportedFormat(Enum):
    """Document formats supported for conversion."""

    # Microsoft Office
    DOCX = ".docx"
    PPTX = ".pptx"
    XLSX = ".xlsx"
    DOC = ".doc"
    PPT = ".ppt"
    XLS = ".xls"

    # OpenDocument
    ODT = ".odt"
    ODP = ".odp"
    ODS = ".ods"

    # Other
    RTF = ".rtf"
    PDF = ".pdf"

    @classmethod
    def is_supported(cls, file_path: Path) -> bool:
        """Check if file format is supported."""
        suffix = file_path.suffix.lower()
        return suffix in [fmt.value for fmt in cls]

    @classmethod
    def requires_pdf_conversion(cls, file_path: Path) -> bool:
        """Check if file needs conversion to PDF."""
        return file_path.suffix.lower() != cls.PDF.value
