# Browser-Based UI Tests for Mesa Visualizations

This directory contains tests that validate Mesa's visualization components using a real browser environment. These tests are slower than the browser-less tests in the parent directory but provide a more thorough validation of the visualization rendering and interaction.

## Setup

To run these tests, you need to install additional dependencies:

```bash
pip install pytest-playwright "pytest-ipywidgets[solara]"
playwright install chromium
```

## Running Tests

Run all UI tests:

```bash
pytest tests/ui -v
```

Run with a specific runner (e.g., only test in Solara):

```bash
pytest tests/ui -v --solara-runner=solara
```

## Updating Reference Snapshots

To update the reference snapshots for visual comparison:

```bash
pytest tests/ui -v --solara-update-snapshots
```

## Snapshot Testing

The tests use visual snapshot comparison to verify that visualization components render correctly. Reference snapshots are stored in the `snapshots` directory.

## Test Organization

- `test_browser_viz.py`: Tests for basic visualization functionality in a browser environment
- `conftest.py`: Configuration for UI tests
- `snapshots/`: Directory for storing reference screenshots

## Continuous Integration

These tests run automatically in the CI pipeline on a weekly schedule and when changes are made to visualization-related code. You can also run them manually via the GitHub Actions "UI Visualization Tests" workflow.

## Troubleshooting

If tests fail with visual differences, examine the test results directory for comparison images to identify what changed. You may need to update the reference snapshots if the changes are expected. 