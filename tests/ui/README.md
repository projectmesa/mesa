# Browser-Based UI Tests for Mesa Visualizations

This directory contains tests that validate Mesa's visualization components in an actual browser environment using Playwright.

## Setup

1. Install the required dependencies:

```bash
pip install -e .[viz-test]
# or explicitly with
pip install pytest pytest-playwright pytest-solara
```

2. Install the Playwright browser:

```bash
playwright install chromium
```

## Running Tests

### Running Locally

```bash
# Run all UI tests
pytest tests/ui/test_browser_viz.py -v

# Run a specific test
pytest tests/ui/test_browser_viz.py::test_schelling_browser -v
```

### Using the Helper Script

```bash
# Run all tests including browser-based tests
./tests/run_viz_tests.sh --ui
```

## Generating Reference Screenshots

The `test_generate_reference_screenshots` test is skipped by default because it's meant to be run manually to update reference images:

```bash
# Generate new reference screenshots
pytest tests/ui/test_browser_viz.py::test_generate_reference_screenshots -v
```

## Troubleshooting

### Common Issues

- **"No browser executable found"**: Run `playwright install chromium`
- **Test timeouts**: Increase timeout with `pytest --timeout=60`
- **Visual differences in screenshots**: Update reference screenshots or adjust comparison threshold

### Headful Mode

To see the browser while tests run:

```bash
pytest tests/ui/test_browser_viz.py --headed
```

## CI Integration

Browser-based tests are configured to run on a manual trigger basis via GitHub Actions workflow in `.github/workflows/ui-viz-tests.yml`.

## Adding New Tests

When adding a new browser-based test:

1. Create a test function that renders your component in a browser context
2. Add appropriate assertions to verify functionality
3. For visual testing, add a reference screenshot
4. Use the `@pytest.mark.skip_if_no_browser` decorator for tests requiring a browser

Example:

```python
@pytest.mark.skip_if_no_browser
def test_new_visualization(browser_page):
    # Test implementation here
    assert model_renders_correctly
```