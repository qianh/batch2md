"""batch2md - Batch Document to Markdown Converter"""

__version__ = "0.1.0"

from .converters import convert_to_pdf, convert_to_markdown, extract_images
from .scanner import scan_documents
from .output_manager import resolve_output_path
from .models import (
    ConversionConfig,
    ConversionJob,
    ConversionSummary,
    ConversionStatus,
    SupportedFormat
)

__all__ = [
    "convert_to_pdf",
    "convert_to_markdown",
    "extract_images",
    "scan_documents",
    "resolve_output_path",
    "ConversionConfig",
    "ConversionJob",
    "ConversionSummary",
    "ConversionStatus",
    "SupportedFormat",
]
