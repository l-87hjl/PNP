#!/bin/bash
#
# Test runner script for PNP lock system
#
# Usage: ./tests/run_tests.sh
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "  PNP Lock System Test Suite"
echo "========================================"
echo

# Check if pytest is installed
if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: pytest not found. Installing...${NC}"
    pip install pytest
fi

# Run tests with verbose output
echo -e "${GREEN}Running tests...${NC}"
echo

python3 -m pytest tests/ -v --tb=short

# Capture exit code
EXIT_CODE=$?

echo
echo "========================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed.${NC}"
fi
echo "========================================"

exit $EXIT_CODE
