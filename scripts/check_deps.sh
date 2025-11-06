#!/bin/bash
# Check system dependencies for batch2md

set -e

echo "============================================================"
echo "batch2md Dependency Check"
echo "============================================================"

EXIT_CODE=0

# Check Python version
echo -e "\n[1/3] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  ✓ $PYTHON_VERSION"
else
    echo "  ✗ Python 3 not found"
    EXIT_CODE=1
fi

# Check LibreOffice
echo -e "\n[2/3] Checking LibreOffice..."
if command -v soffice &> /dev/null; then
    LIBREOFFICE_VERSION=$(soffice --version 2>&1 | head -n 1)
    echo "  ✓ $LIBREOFFICE_VERSION"
else
    echo "  ✗ LibreOffice not found"
    echo "     Install with:"
    echo "     macOS:  brew install libreoffice"
    echo "     Ubuntu: sudo apt-get install libreoffice"
    EXIT_CODE=1
fi

# Check MinerU
echo -e "\n[3/3] Checking MinerU..."
if python3 -c "import mineru" 2>/dev/null; then
    MINERU_VERSION=$(python3 -c "import mineru; print(mineru.__version__ if hasattr(mineru, '__version__') else 'installed')" 2>/dev/null || echo "installed")
    echo "  ✓ MinerU $MINERU_VERSION"

    # Check if models are downloaded
    if [ -d "$HOME/.mineru/models" ] || [ -d "$HOME/.magic-pdf/models" ]; then
        echo "  ✓ MinerU models found"
    else
        echo "  ⚠ MinerU models not downloaded"
        echo "     Run: mineru download"
    fi
else
    echo "  ✗ MinerU not installed"
    echo "     Install with: pip install mineru"
    echo "     Then download models: mineru download"
    EXIT_CODE=1
fi

# Summary
echo -e "\n============================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All dependencies are installed!"
    echo "============================================================"
    echo -e "\nYou can now:"
    echo "  1. Create test fixtures: python scripts/create_fixtures.py"
    echo "  2. Install package: pip install -e ."
    echo "  3. Run tests: pytest tests/ -v"
else
    echo "✗ Some dependencies are missing"
    echo "============================================================"
    echo -e "\nPlease install missing dependencies and run this script again."
fi

exit $EXIT_CODE
