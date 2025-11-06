# Test Fixtures

This directory contains sample documents for testing.

## Required Test Documents

For comprehensive testing, please create or add the following files:

### Basic Documents
- `simple.docx` - Plain text document (1 page)
- `simple.txt` - Plain text file for conversion testing

### Complex Documents
- `with_table.docx` - Document containing tables
- `with_images.docx` - Document with embedded images
- `presentation.pptx` - Sample PowerPoint presentation
- `spreadsheet.xlsx` - Sample Excel spreadsheet

### Pre-converted
- `sample.pdf` - Pre-made PDF for direct Markdown conversion

### Error Testing
- `corrupted.docx` - Intentionally corrupted file for error handling tests

### Nested Structure
- `nested/sample.docx` - Document in subdirectory for recursive testing

## Creating Test Documents

### Quick Setup with LibreOffice

```bash
# Create a simple text file
echo "This is a test document." > simple.txt

# Convert to DOCX using LibreOffice
soffice --headless --convert-to docx simple.txt --outdir tests/fixtures/

# Create nested test document
cp tests/fixtures/simple.docx tests/fixtures/nested/
```

### Manual Creation

Alternatively, create these documents manually using:
- Microsoft Office
- LibreOffice
- Google Docs (export as Office format)

### Minimal Setup

For basic testing, at minimum you need:
1. `simple.txt` - Can be created by the script
2. One DOCX file - Will be generated from simple.txt
3. One corrupted file - Can be created by corrupting a valid file

## Automated Setup Script

Run the setup script to create basic test fixtures:

```bash
python scripts/create_fixtures.py
```

This will create:
- Simple text documents
- Convert them to various Office formats
- Create a nested directory structure
- Generate a corrupted file for error testing
