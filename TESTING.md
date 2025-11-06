# Testing Documentation

## Test Structure

This project follows **Test-Driven Development (TDD)** as mandated by the SDD Constitution Article III.

### Test Organization

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── fixtures/                # Test documents
│   ├── simple.txt
│   ├── nested/
│   └── README.md
├── test_cli_contract.py     # CLI interface tests (17 tests)
├── test_scanner.py          # Document scanner tests (11 tests)
├── test_doc2pdf.py          # Doc→PDF conversion tests (13 tests)
├── test_pdf2md.py           # PDF→Markdown tests (20 tests)
├── test_output_manager.py   # Output management tests (20 tests)
└── test_integration.py      # End-to-end tests (20 tests)
```

**Total: ~101 test cases**

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Fast, isolated tests
- No external dependencies (LibreOffice, MinerU)
- Test individual functions and modules

### Integration Tests (`@pytest.mark.integration`)
- Require external tools (LibreOffice, MinerU)
- Test real document conversions
- May be skipped if dependencies not installed

### Slow Tests (`@pytest.mark.slow`)
- Performance tests
- Large batch processing
- Optional for quick test runs

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Unit Tests Only (Fast)
```bash
pytest tests/ -v -m unit
```

### Integration Tests Only
```bash
pytest tests/ -v -m integration
```

### Exclude Slow Tests
```bash
pytest tests/ -v -m "not slow"
```

### With Coverage
```bash
pytest tests/ --cov=batch2md --cov-report=html
```

### Specific Test File
```bash
pytest tests/test_scanner.py -v
```

## Test Coverage Requirements

- **Minimum: 80% code coverage**
- All critical paths must be tested
- Error handling must be tested

## Test Phase Status

### Phase 2: Test Creation ✅

- [x] Phase 2.1: CLI Contract Tests (17 tests)
- [x] Phase 2.2: Scanner Tests (11 tests)
- [x] Phase 2.3: Doc→PDF Tests (13 tests)
- [x] Phase 2.4: PDF→Markdown Tests (20 tests)
- [x] Phase 2.5: Output Manager Tests (20 tests)
- [x] Phase 2.6: Integration Tests (20 tests)
- [ ] Phase 2.7: Run Tests (Expected to FAIL - no implementation yet)
- [ ] Phase 2.8: User Approval Required

### Phase 3: Implementation (Pending Approval)

⚠️ **IMPORTANT**: No implementation code will be written until:
1. All tests are reviewed and approved
2. Tests are confirmed to fail (red phase)
3. User gives explicit approval to proceed

## Expected Test Results (Current State)

Since implementation is not yet complete, tests should FAIL with:
- `AttributeError`: Functions not defined
- `ImportError`: Modules not implemented
- `NotImplementedError`: Stub functions

This is **EXPECTED** and **CORRECT** per TDD methodology.

## Test Dependencies

### Required for All Tests
- Python 3.8+
- pytest >= 7.0.0

### Required for Integration Tests
- LibreOffice (soffice command)
- MinerU >= 2.0.0
- MinerU models downloaded (`mineru download`)

### Check Dependencies
```bash
# Run dependency check
bash scripts/check_deps.sh

# Create test fixtures (requires LibreOffice)
python scripts/create_fixtures.py
```

## Test Fixtures

Test fixtures are located in `tests/fixtures/`:

- `simple.txt` - Plain text for basic tests
- `nested/sample.txt` - Tests recursive scanning
- Additional fixtures can be created with `scripts/create_fixtures.py`

### Creating Real Test Documents

For full integration testing, you'll need:
1. DOCX with tables
2. DOCX with images
3. PPTX presentation
4. XLSX spreadsheet
5. Corrupted DOCX for error testing

Use `scripts/create_fixtures.py` to generate these automatically.

## Continuous Integration

### Pre-commit Checks
```bash
# Run before committing
pytest tests/ -v -m "not slow"
black src/ tests/
flake8 src/ tests/
mypy src/
```

### CI Pipeline (GitHub Actions example)
```yaml
- name: Run Tests
  run: |
    pytest tests/ -v -m unit --cov=batch2md
    pytest tests/ -v -m "integration and not slow"
```

## Troubleshooting

### Tests Skip Due to Missing Dependencies

**Problem**: Tests are skipped with "LibreOffice not available"

**Solution**:
```bash
# macOS
brew install libreoffice

# Ubuntu
sudo apt-get install libreoffice

# Verify
which soffice
```

**Problem**: Tests are skipped with "MinerU not installed"

**Solution**:
```bash
pip install mineru
mineru download  # Download models
python3 -c "import mineru"  # Verify
```

### Tests Fail with Import Errors

**Problem**: `ModuleNotFoundError: No module named 'batch2md'`

**Solution**:
```bash
# Install in development mode
pip install -e .
```

### Tests Hang or Timeout

**Problem**: LibreOffice conversion hangs

**Solution**:
```bash
# Kill any stuck soffice processes
pkill soffice
```

## Test-First Workflow

As per SDD Constitution Article III:

1. ✅ **Write Tests First** - Tests define requirements
2. ⚠️ **Get User Approval** - User reviews and approves test scenarios
3. ✅ **Confirm Red** - Tests must fail before implementation
4. ⏳ **Implement** - Write code to make tests pass
5. ⏳ **Confirm Green** - All tests must pass
6. ⏳ **Refactor** - Improve code while keeping tests green

**Current Status**: Step 3 - Ready for confirmation that tests fail

## Next Steps

1. **Run tests** to confirm they fail appropriately
2. **User reviews** test coverage and scenarios
3. **User approves** test suite
4. **Begin implementation** (Phase 3)

---

**Note**: This testing strategy ensures that:
- Requirements are clearly defined via tests
- Implementation matches specifications
- No feature creep or unnecessary code
- High code quality and maintainability
