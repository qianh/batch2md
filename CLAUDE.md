# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**batch2md** is a CLI tool that batch converts documents (DOCX, PPTX, XLSX, ODT, PDF, RTF) to Markdown via a two-stage pipeline: Document → PDF (LibreOffice) → Markdown (MinerU).

### Critical External Dependencies

- **LibreOffice** (`soffice` command): Required for converting office documents to PDF
- **MinerU** (Python package + models): Required for high-quality PDF→Markdown conversion
  - Models must be downloaded once: `mineru download` (~500MB)

## Development Commands

### Installation

This project uses **uv** for package and environment management.

```bash
# Install dependencies and create virtual environment
uv sync

# Install with development tools (testing, linting)
uv sync --extra dev

# Alternative: using pip (legacy)
pip install -e .
pip install -e ".[dev]"
```

### Environment Management
```bash
# Activate virtual environment (uv manages this automatically)
source .venv/bin/activate

# Or use uv run to execute commands directly
uv run python -m batch2md --help

# Install specific Python version
uv python install 3.10
```

### Testing
```bash
# Run all tests (69 pass, 17 skip due to missing test fixtures)
uv run pytest tests/ -v

# Run specific test categories
uv run pytest tests/ -v -m unit                    # Unit tests only
uv run pytest tests/ -v -m integration             # Integration tests
uv run pytest tests/ -v -m "not slow"              # Exclude slow tests

# Run single test file
uv run pytest tests/test_scanner.py -v

# With coverage report
uv run pytest tests/ --cov=batch2md --cov-report=html

# Run single test function
uv run pytest tests/test_scanner.py::test_scan_finds_docx_files -v
```

### Running the Tool
```bash
# As installed command (after pip install)
batch2md /path/to/documents

# As Python module
python -m batch2md /path/to/documents

# Common flags
batch2md /path/to/docs --verbose           # Detailed output
batch2md /path/to/docs --dry-run           # Preview only
batch2md /path/to/docs --no-recursive      # Top-level only
batch2md /path/to/docs --backend vlm       # Use vision-language model
```

### Code Quality
```bash
# Format code
uv run black src/ tests/

# Lint
uv run flake8 src/ tests/

# Type checking
uv run mypy src/
```

## Architecture

### Conversion Pipeline Flow

```
1. Scanner (scanner.py)
   - Recursively discover supported document files
   - Filter by SupportedFormat enum

2. Doc→PDF Converter (converters.py:convert_to_pdf)
   - Call LibreOffice headless: soffice --headless --convert-to pdf
   - Validate PDF output (magic bytes %PDF, minimum size)
   - Skip if input is already PDF

3. PDF→Markdown Converter (converters.py:convert_to_markdown)
   - Call MinerU CLI: mineru pdf input.pdf -o output_dir --backend pipeline
   - MinerU creates complex subdirectory structure
   - Code searches multiple possible locations to find generated .md file
   - Move .md to expected output location

4. Image Extractor (converters.py:extract_images)
   - MinerU extracts images during conversion (not separate step)
   - Search output directory tree for image files
   - Rename to pattern: {document_stem}_img{N}.{ext}
   - Copy to centralized images/ directory

5. Output Manager (output_manager.py)
   - Mirror input directory structure in output/markdown/
   - Resolve conflicts with timestamp suffix: filename_20251105_143022.md
   - Place all images in single images/ directory at markdown root
```

### Key Design Patterns

**Data Models (models.py)**
- `ConversionJob`: Tracks single document conversion with status (PENDING → CONVERTING_TO_PDF → CONVERTING_TO_MD → COMPLETED/FAILED)
- `ConversionSummary`: Aggregates batch results, calculates exit codes (0=success, 1=partial, 2=total failure)
- `ConversionConfig`: CLI arguments as dataclass
- `SupportedFormat`: Enum of file extensions with helper methods

**Error Handling Philosophy**
- Individual file failures don't stop batch processing
- All exceptions caught and stored in ConversionJob.error
- Summary report shows both successes and failures
- Exit codes indicate overall batch status

**CLI Flow (cli.py:run_conversion)**
```python
1. scan_documents() → List[Path]
2. For each document:
   a. resolve_output_path() with conflict handling
   b. convert_to_pdf() if not PDF
   c. convert_to_markdown() via MinerU
   d. extract_images() from MinerU output
   e. Store job in completed_jobs or failed_jobs
3. Return ConversionSummary with statistics
```

### MinerU Integration Quirks

**Critical Implementation Details:**

1. **Output Location Mystery**: MinerU doesn't document its output structure clearly. The code searches these locations in order:
   - `{output_dir}/{pdf_stem}.md`
   - `{output_dir}/{pdf_stem}/auto/{pdf_stem}.md`
   - `{output_dir}/auto/{pdf_stem}.md`
   - Falls back to recursive search: `output_dir.rglob("*.md")`

2. **Image Handling**: Images are extracted during `mineru pdf` conversion, not as separate step. The `extract_images()` function is actually a post-processing search that:
   - Scans the entire MinerU output tree
   - Finds all image files
   - Renames and consolidates them

3. **Backend Options**:
   - `pipeline`: Default, fastest, CPU-only
   - `vlm`: Vision-language model, better accuracy, slower
   - `vllm`: GPU-accelerated inference (requires GPU)

## Test Structure

Tests follow **Test-Driven Development (TDD)** - they were written before implementation.

**Test Categories (pytest markers):**
- `@pytest.mark.unit` - Fast, no external dependencies
- `@pytest.mark.integration` - Requires LibreOffice/MinerU
- `@pytest.mark.slow` - Performance tests (batch 100 documents)

**17 tests currently skip** due to missing test fixtures (PPTX, XLSX, images). These can be created with real documents if needed.

**Test fixtures in `tests/fixtures/`:**
- Very minimal currently (simple.txt, nested/)
- Integration tests dynamically create temporary test documents
- Real document fixtures would improve test coverage

## Common Development Scenarios

### Adding Support for New Format

1. Add extension to `SupportedFormat` enum in models.py
2. Verify LibreOffice supports it (check LibreOffice docs)
3. Add test case in `test_doc2pdf.py`
4. No code changes needed if LibreOffice supports it

### Debugging Conversion Failures

```bash
# Enable verbose mode to see subprocess output
batch2md /path --verbose

# Check LibreOffice manually
soffice --headless --convert-to pdf --outdir /tmp /path/to/doc.docx
ls /tmp/*.pdf

# Check MinerU manually
mineru pdf /tmp/doc.pdf -o /tmp/output
ls /tmp/output/**/*.md
```

### Adding New CLI Option

1. Add argument in `cli.py:parse_args()` using argparse
2. Add field to `ConversionConfig` dataclass in models.py
3. Use config field in `cli.py:run_conversion()`
4. Add test in `test_cli_contract.py`

## Project Metadata

- **Python**: 3.10+ required (MinerU dependency)
- **Package Structure**: `src` layout (not flat)
- **Entry Point**: `batch2md` command → `batch2md.main:main`
- **Module Execution**: `python -m batch2md` supported via `__main__.py`

## SDD Methodology Context

This project was developed using Specification-Driven Development (SDD):
- Specifications in `/Users/john/.claude/skills/sdd-development/specs/001-batch-document-to-markdown/`
- Tests written first (101 tests), then implementation
- No abstraction layers - direct use of LibreOffice and MinerU
- Single library (no microservices or multiple packages)

When making changes, preserve these principles:
- Direct framework usage (no unnecessary wrappers)
- Simple data structures (dataclasses, no ORM)
- Test coverage for new features
- Error messages reference actual commands user can run
