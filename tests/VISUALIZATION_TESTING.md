# Mesa Visualization Testing Strategy

This document outlines the approach to testing Mesa's visualization components (SolaraViz) to ensure visualization functionality works correctly across all example models.

## Testing Approach

The visualization testing strategy consists of three main components:

1. **Unit Tests (Browser-less)**: Fast tests that validate individual visualization components without requiring a browser.
2. **Performance Benchmarks**: Measure rendering performance across different visualization backends and model sizes.
3. **Browser-Based UI Tests**: Comprehensive tests that validate visualization rendering and interaction in a real browser environment.

## Test Organization

- `test_solara_viz.py`: Tests for the SolaraViz component's core functionality
- `test_visualization_components.py`: Tests for individual visualization components (matplotlib, altair)
- `ui/test_browser_viz.py`: Browser-based tests for visualization rendering and interaction
- `run_viz_tests.sh`: Helper script for running visualization tests

## Running Tests

To run all visualization tests:

```bash
./tests/run_viz_tests.sh
```

To include browser-based UI tests:

```bash
./tests/run_viz_tests.sh --ui
```

To run performance benchmarks:

```bash
./tests/run_viz_tests.sh --benchmarks
```

To update UI snapshot references:

```bash
./tests/run_viz_tests.sh --ui --update-snapshots
```

## Continuous Integration

Visualization tests are integrated into the CI pipeline:

1. `viz-tests.yml`: Runs browser-less tests on every PR and push to main branches
2. `ui-viz-tests.yml`: Runs browser-based tests weekly and on PRs that change visualization code

## Dependencies

Visualization tests require additional dependencies beyond the core Mesa package:

```bash
pip install -e .[viz,dev]          # For browser-less tests
pip install -e .[viz-test]         # For browser-based tests
playwright install chromium        # For browser-based tests
```

## Test Coverage

The visualization tests cover:

1. **Component Rendering**: Testing that visualization components render correctly
2. **Model Interaction**: Testing model stepping, play/pause, and reset functionality
3. **Parameter Controls**: Testing that user input controls work correctly
4. **Performance**: Benchmarking visualization performance
5. **Cross-Model Compatibility**: Testing visualization components across all example models

## Snapshot Testing

Browser-based tests use snapshot testing to compare rendered visualizations against reference images. This ensures visual consistency across code changes.

To update reference snapshots:

```bash
pytest tests/ui/ --solara-update-snapshots --solara-runner=solara
```

## Adding New Tests

When adding new visualization components:

1. Add browser-less tests to `test_visualization_components.py`
2. Add performance benchmarks for significant new components
3. Add browser-based tests for components with complex UI interaction
4. Ensure CI workflows run the new tests

## Troubleshooting

If visualization tests fail:

1. Check dependency versions (especially solara, matplotlib, altair)
2. For snapshot failures, compare the test results in `test-results/` with the reference images
3. Update reference snapshots if the visual changes are expected
4. For browser-based test failures, try running with `--headed` flag to see the browser 