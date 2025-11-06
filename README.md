# batch2md - Batch Document to Markdown Converter

Convert document collections (DOCX, PPTX, XLSX, etc.) to Markdown via PDF using MinerU.

## Features

- 📄 **Multi-format support**: DOCX, PPTX, XLSX, ODT, ODP, ODS, RTF, PDF
- 🔄 **Batch processing**: Convert entire directories with one command
- 📁 **Recursive scanning**: Process nested folder structures
- 🖼️ **Image extraction**: Extract and reference images from documents
- 📊 **Table preservation**: Convert tables to Markdown format
- ⚡ **High-quality conversion**: Uses MinerU for superior PDF-to-Markdown conversion
- 🛡️ **Error handling**: Continues processing even if individual files fail
- 📈 **Progress reporting**: Real-time conversion status

## Installation

> **Note**: This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management. You can also use pip if you prefer.

### Prerequisites

1. **Python 3.10+** (MinerU requirement)

2. **LibreOffice** (for document-to-PDF conversion)
   ```bash
   # macOS
   brew install libreoffice

   # Ubuntu/Debian
   sudo apt-get install libreoffice

   # Verify installation
   which soffice
   ```

3. **MinerU** (for PDF-to-Markdown conversion)
   ```bash
   pip install mineru

   # Download models (one-time, ~500MB)
   mineru download
   ```

### Install batch2md

```bash
# Using uv (recommended - 10-100x faster than pip)
git clone <repository-url>
cd batch2md
uv sync                    # Install dependencies
uv sync --extra dev        # Include development tools

# Or using pip (traditional method)
pip install -e .           # Install in development mode
pip install -e ".[dev]"    # Include development tools

# Or from PyPI (when available)
pip install batch2md
```

**Why uv?**
- ⚡ 10-100x faster package installation
- 🔒 Reproducible builds with lock file
- 🐍 Automatic Python version management
- 💪 Drop-in replacement for pip

## Usage

### Basic Usage

```bash
# Convert all documents in a directory
batch2md /path/to/documents

# Output will be in: /path/to/documents/markdown/
```

### Command-Line Options

```bash
batch2md [OPTIONS] INPUT_DIR

Options:
  --output DIR          Custom output directory (default: INPUT_DIR/markdown/)
  --no-recursive        Process only top-level files, skip subdirectories
  --verbose, -v         Show detailed progress information
  --dry-run             Preview what would be converted without converting
  --backend BACKEND     MinerU backend: pipeline (default), vlm, or vllm
  --json                Output results as JSON
  --help, -h            Show help message
```

### Examples

```bash
# Convert with verbose output
batch2md ~/Documents/reports --verbose

# Non-recursive (top-level only)
batch2md ~/Documents --no-recursive

# Custom output location
batch2md ~/Documents --output ~/Markdown

# Dry run to preview
batch2md ~/Documents --dry-run

# Use vision-language model backend (better accuracy, slower)
batch2md ~/Documents --backend vlm
```

## Output Structure

```
input_dir/
├── document1.docx
├── document2.pptx
├── subdir/
│   └── document3.xlsx
└── markdown/                    # Output directory
    ├── document1.md
    ├── document2.md
    ├── subdir/
    │   └── document3.md
    └── images/                  # Extracted images
        ├── document1_img1.png
        ├── document2_img1.png
        └── subdir_document3_img1.png
```

## Supported Formats

| Format | Extension | Conversion Method |
|--------|-----------|------------------|
| Microsoft Word | .docx, .doc | LibreOffice → PDF → Markdown |
| Microsoft PowerPoint | .pptx, .ppt | LibreOffice → PDF → Markdown |
| Microsoft Excel | .xlsx, .xls | LibreOffice → PDF → Markdown |
| OpenDocument Text | .odt | LibreOffice → PDF → Markdown |
| OpenDocument Presentation | .odp | LibreOffice → PDF → Markdown |
| OpenDocument Spreadsheet | .ods | LibreOffice → PDF → Markdown |
| Rich Text Format | .rtf | LibreOffice → PDF → Markdown |
| PDF | .pdf | Direct conversion with MinerU |

## Features in Detail

### Table Preservation

Tables in source documents are converted to Markdown table syntax:

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
```

### Image Extraction

Images are extracted to a separate `images/` directory and referenced in Markdown:

```markdown
![](images/document_img1.png)
```

### File Conflict Handling

If an output file already exists, a timestamp suffix is added automatically:

```
Existing: document.md
New:      document_20251105_143022.md
```

### Error Handling

Conversion continues even if individual files fail. Summary shows both successful and failed conversions:

```
Processing [1/3]: good.docx ✓
Processing [2/3]: corrupted.docx ✗ Failed: File is corrupted
Processing [3/3]: another.docx ✓

Summary: 2/3 files converted successfully, 1 failed
```

## Performance

Typical conversion times (approximate):
- Single DOCX (10 pages): < 10 seconds
- Single PPTX (20 slides): < 15 seconds
- Batch 100 documents: < 10 minutes

Performance depends on:
- Document size and complexity
- MinerU backend (pipeline is fastest)
- System resources (CPU, RAM)

## Troubleshooting

### LibreOffice not found

```bash
# Verify installation
which soffice

# If not found, install LibreOffice (see Installation section)
```

### MinerU errors

```bash
# Re-download models
rm -rf ~/.mineru/models
mineru download

# Verify installation
pip show mineru
mineru --help
```

### Permission errors

```bash
# Ensure write permissions
chmod +w /path/to/output/dir
```

### Memory issues with large files

Try processing files in smaller batches or use a system with more RAM.

## Development

### Running Tests

```bash
# Install development dependencies (uv)
uv sync --extra dev

# Or using pip
pip install -e ".[dev]"

# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=batch2md
```

### Project Structure

```
batch2md/
├── src/batch2md/           # Source code
│   ├── __init__.py
│   ├── cli.py             # CLI interface
│   ├── converters.py      # Conversion logic
│   ├── scanner.py         # Document scanner
│   ├── models.py          # Data models
│   └── main.py            # Entry point
├── tests/                 # Test suite
│   ├── fixtures/          # Test documents
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
└── scripts/               # Utility scripts
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [MinerU](https://github.com/opendatalab/MinerU) - High-quality PDF extraction
- [LibreOffice](https://www.libreoffice.org/) - Document conversion

## Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Documentation: <repository-url>/docs
