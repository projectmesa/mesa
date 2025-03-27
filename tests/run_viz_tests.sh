#!/bin/bash
# Helper script to run visualization component tests

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

# Parse arguments
RUN_UI=false
RUN_BENCHMARKS=false
VERBOSE=false

for arg in "$@"; do
  case $arg in
    --ui)
      RUN_UI=true
      shift
      ;;
    --benchmarks)
      RUN_BENCHMARKS=true
      shift
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    *)
      # Unknown option
      ;;
  esac
done

# Define verbosity flag
VERBOSITY=""
if [ "$VERBOSE" = true ]; then
  VERBOSITY="-v"
fi

echo "🧪 Running Mesa visualization component tests..."

# Run browser-less tests first
BROWSER_LESS_RESULT=0
if [ "$RUN_BENCHMARKS" = true ]; then
  echo "🔍 Running performance benchmarks..."
  python -m pytest tests/test_visualization_components.py::test_performance_benchmarks $VERBOSITY || BROWSER_LESS_RESULT=$?
else
  echo "🔍 Running browser-less visualization tests..."
  python -m pytest tests/test_visualization_components.py $VERBOSITY || BROWSER_LESS_RESULT=$?
fi

# Run browser-based tests if requested
UI_RESULT=0
if [ "$RUN_UI" = true ]; then
  # Check if playwright is installed
  if ! command -v playwright &> /dev/null; then
    echo "⚠️  Playwright not found. Installing required browser..."
    playwright install chromium
  fi
  
  echo "🌐 Running browser-based UI tests..."
  python -m pytest tests/ui/test_browser_viz.py $VERBOSITY || UI_RESULT=$?
fi

# Output test summary
echo ""
echo "📊 Test Summary:"
echo "----------------"
if [ $BROWSER_LESS_RESULT -eq 0 ]; then
  echo "✅ Browser-less tests: PASSED"
else
  echo "❌ Browser-less tests: FAILED"
fi

if [ "$RUN_UI" = true ]; then
  if [ $UI_RESULT -eq 0 ]; then
    echo "✅ Browser-based tests: PASSED"
  else
    echo "❌ Browser-based tests: FAILED"
  fi
fi

# Exit with failure if any test suite failed
if [ $BROWSER_LESS_RESULT -ne 0 ] || [ $UI_RESULT -ne 0 ]; then
  exit 1
fi

exit 0 