# Add Comprehensive Testing for Mesa's Visualization Components

## Overview
This PR adds a robust testing infrastructure for Mesa's visualization components (SolaraViz) to ensure they render correctly and function properly across all example models.

## Key Additions

### Browser-less Unit Tests (`test_visualization_components.py`)
- Tests for both Matplotlib and Altair visualization backends
- Component-level tests for space and plot visualizations
- Cross-model tests to verify visualization functionality in all example models
- Interactive testing of model controllers (step, play/pause, reset)
- Performance benchmarks to measure rendering efficiency

### Browser-based UI Tests (`tests/ui/test_browser_viz.py`) - Manual Execution Only
- Integration tests for end-to-end visualization rendering
- Visual regression testing via screenshot comparisons
- Tests for parameter controls and interactive features
- Compatibility with Solara's recommended testing approach

**Note**: Browser-based tests require additional dependencies (`playwright`) and are configured to run only manually or on a weekly schedule, not on every PR.

### CI Integration
- Added `viz-tests.yml` for fast browser-less tests on all PRs
- Added `ui-viz-tests.yml` for periodic browser-based testing (weekly + manual triggers)
- Coverage reporting for visualization components

### Developer Tools
- Added `run_viz_tests.sh` helper script for local testing
- Created `VISUALIZATION_TESTING.md` documentation
- Updated `pyproject.toml` with testing dependencies

## How It Works

The testing approach follows Solara's recommended practices for testing without a browser:

```python
def test_example():
    # 1. Set up test model
    model = Schelling(seed=42)

    # 2. Create and render visualization component
    component = make_altair_space(agent_portrayal)
    box, rc = solara.render(component(model), handle_error=False)

    # 3. Find and verify UI elements
    assert rc.find("div").widget is not None

    # 4. Test model interaction
    step_button = rc.find(v.Btn, children=["Step"]).widget
    step_button.click()
    assert model.schedule.steps > 0
```

This approach allows us to thoroughly test visualization components without requiring a browser in CI, while still providing browser-based tests for more comprehensive validation when needed.

## Running Tests Locally

```bash
# Run browser-less tests
./tests/run_viz_tests.sh

# Run with browser-based UI tests (requires additional dependencies)
pip install -e .[viz-test]
playwright install chromium
./tests/run_viz_tests.sh --ui

# Run performance benchmarks
./tests/run_viz_tests.sh --benchmarks
```

## Benefits
- Ensures visualization components render correctly across all examples
- Provides performance metrics for visualization rendering
- Prevents regressions in visualization functionality
- Follows Solara's recommended testing practices

These tests address the current gap where basic model execution is tested but visualization functionality is not systematically verified.