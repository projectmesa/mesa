# Testing Mesa's Visualization Components

This document explains how Mesa's visualization components are tested and how you can run or extend these tests.

## Testing Approach

Mesa's visualization components are tested using two complementary approaches:

1. **Browser-less Unit Tests**: Fast tests that validate component functionality without requiring a browser
2. **Browser-based UI Tests**: Full integration tests that validate rendering and interaction in an actual browser

### Browser-less Unit Tests

Located in `tests/test_visualization_components.py`, these tests:

- Render components using Solara's test utilities without a browser
- Test both Matplotlib and Altair visualization backends
- Verify component properties, rendering logic, and interactive features
- Include performance benchmarks for visualization rendering

These tests run quickly and are ideal for CI pipelines.

### Browser-based UI Tests

Located in `tests/ui/test_browser_viz.py`, these tests:

- Use Playwright to render components in an actual browser environment
- Perform visual regression testing via screenshot comparisons
- Test complex interactions that require a real browser
- Validate end-user experience with Mesa visualizations

These tests require additional dependencies and are designed to run less frequently (weekly or on-demand).

## Running Tests Locally

### Setup

1. Install the testing dependencies:

```bash
# Install base testing dependencies
pip install -e ".[test]"

# For browser-based tests, also install:
pip install -e ".[viz-test]"
playwright install chromium
```

### Running Tests

```bash
# Run all tests (excluding browser tests)
pytest tests/test_visualization_components.py -v

# Run browser-based tests
pytest tests/ui/test_browser_viz.py -v

# Run tests with the helper script
./tests/run_viz_tests.sh         # Browser-less tests only
./tests/run_viz_tests.sh --ui    # Include browser tests
./tests/run_viz_tests.sh --benchmarks  # Run performance benchmarks
```

## CI Integration

Testing is integrated into the CI pipeline with two workflows:

1. **Standard Tests** (`viz-tests.yml`): Runs browser-less tests on all PRs and commits
2. **UI Tests** (`ui-viz-tests.yml`): Runs browser-based tests on manual trigger or weekly schedule

## Test Coverage

The test suite covers:

- **Component Creation**: Tests for all visualization component types
- **Model Integration**: Tests with all example models (Schelling, Conway, Boids, etc.)
- **Interactive Features**: Tests for step buttons, sliders, reset buttons
- **Visual Appearance**: Tests for color schemes, layouts, and responsive behavior
- **Performance**: Benchmarks for rendering speed across different models and settings

## Adding New Tests

### Adding a Browser-less Test

1. Add your test to `tests/test_visualization_components.py`
2. Focus on component logic, properties, and basic rendering
3. Use Solara's test utilities: `solara.render()`

Example:

```python
def test_new_component():
    component = make_plot_component({"Data": "blue"})
    box, rc = solara.render(component(model), handle_error=False)
    assert rc.find("div").widget is not None
```

### Adding a Browser-based Test

1. Add your test to `tests/ui/test_browser_viz.py`
2. Use the Playwright utilities for browser interaction
3. Consider adding visual regression tests for new components

Example:

```python
@pytest.mark.skip_if_no_browser
def test_new_component_browser(browser_page):
    # Test implementation
    screenshot = browser_page.screenshot()
    assert_screenshot_matches(screenshot, "reference_screenshot.png")
```

## Best Practices

1. **Test Both Backends**: Always test both Matplotlib and Altair components
2. **Use Seeds**: Set random seeds in tests for deterministic results
3. **Test Responsiveness**: Ensure components work at different sizes
4. **Performance**: Include performance tests for computationally intensive visualizations
5. **Visual Testing**: Use screenshot assertions only for critical visual elements

## Troubleshooting

- **Failed Visual Tests**: Examine the screenshot differences and update references if needed
- **Slow Tests**: Use the `--benchmark-only` flag to identify performance bottlenecks
- **Browser Issues**: Try running with `--headed` flag to observe browser behavior