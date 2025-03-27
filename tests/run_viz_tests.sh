#!/bin/bash
# Helper script to run visualization tests

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}Mesa Visualization Tests Runner${NC}"
echo "=============================="

# Process command line options
RUN_UI=false
UPDATE_SNAPSHOTS=false
RUN_BENCHMARKS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --ui)
            RUN_UI=true
            shift
            ;;
        --update-snapshots)
            UPDATE_SNAPSHOTS=true
            shift
            ;;
        --benchmarks)
            RUN_BENCHMARKS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--ui] [--update-snapshots] [--benchmarks]"
            exit 1
            ;;
    esac
done

# Check if required dependencies are installed
check_dependency() {
    if ! python -c "import $1" &> /dev/null; then
        echo -e "${YELLOW}Warning: $1 is not installed. Some tests may fail.${NC}"
        echo "Install with: pip install -e .[viz${2:+,$2}]"
        echo ""
    fi
}

check_dependency "solara" "viz"
check_dependency "matplotlib" "viz"
check_dependency "pytest" "dev"

# Run the regular visualization tests
echo -e "${GREEN}Running browser-less visualization tests...${NC}"
python -m pytest -xvs tests/test_visualization_components.py tests/test_solara_viz.py

# Run benchmarks if requested
if [ "$RUN_BENCHMARKS" = true ]; then
    echo -e "\n${GREEN}Running visualization benchmarks...${NC}"
    python -m pytest -xvs tests/test_visualization_components.py::TestPerformanceBenchmarks
fi

# Run UI tests if requested
if [ "$RUN_UI" = true ]; then
    # Check for UI test dependencies
    check_dependency "playwright" "viz-test"
    check_dependency "pytest_ipywidgets" "viz-test"
    
    # Ensure Playwright browsers are installed
    if ! python -c "from playwright.sync_api import sync_playwright; sync_playwright().start().stop()" &> /dev/null; then
        echo -e "${YELLOW}Installing Playwright browsers...${NC}"
        python -m playwright install chromium
    fi
    
    # Run the UI tests
    echo -e "\n${GREEN}Running browser-based UI tests...${NC}"
    if [ "$UPDATE_SNAPSHOTS" = true ]; then
        python -m pytest -xvs tests/ui/ --solara-runner=solara --solara-update-snapshots
    else
        python -m pytest -xvs tests/ui/ --solara-runner=solara
    fi
fi

echo -e "\n${GREEN}Visualization tests completed!${NC}" 