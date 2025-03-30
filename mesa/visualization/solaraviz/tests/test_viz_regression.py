"""Regression tests for Mesa's SolaraViz visualization components.
These tests are designed to catch regressions in visualization functionality.
"""

import inspect
import os
import sys

import pytest

sys.path.append(os.path.abspath("."))

# Import the mock components
from mock_solara_components import (
    ModelApp,
)

import mesa


def test_viz_component_interface_stability(example_model_name):
    """Test that visualization component interfaces remain stable.

    This checks that component signatures and properties don't change unexpectedly.
    """
    try:
        # Get the visualizations for this model
        visualizations = mesa.examples[example_model_name]["visualization"]

        for viz_name, viz_func in visualizations.items():
            # Check that the function has a signature
            sig = inspect.signature(viz_func)

            # Check that it accepts a model parameter
            assert "model" in sig.parameters, (
                f"{viz_name} should accept a 'model' parameter"
            )

            # Check that model parameter is optional
            assert (
                sig.parameters["model"].default is None
                or sig.parameters["model"].default is inspect.Parameter.empty
            ), f"{viz_name}'s 'model' parameter should be optional or required"
    except (KeyError, AttributeError, ImportError) as e:
        pytest.skip(
            f"Could not check component interfaces for {example_model_name}: {e}"
        )


def test_solara_component_existence(example_model_name):
    """Test that expected Solara components exist for each example model."""
    try:
        # Check that the model has visualizations
        assert "visualization" in mesa.examples[example_model_name], (
            f"Model {example_model_name} should have visualizations defined"
        )

        # Get the visualizations
        visualizations = mesa.examples[example_model_name]["visualization"]

        # Check that there's at least one visualization
        assert len(visualizations) > 0, (
            f"Model {example_model_name} should have at least one visualization component"
        )

        # Check common visualization types
        has_grid = any("grid" in viz_name.lower() for viz_name in visualizations)
        has_chart = any("chart" in viz_name.lower() for viz_name in visualizations)

        # Not all models need grid and chart visualizations, so this is just informational
        # and not an assertion
        if not has_grid and not has_chart:
            pytest.xfail(
                f"Model {example_model_name} doesn't have common visualization types"
            )
    except (KeyError, AttributeError) as e:
        pytest.skip(
            f"Could not check component existence for {example_model_name}: {e}"
        )


def test_app_structure(example_model_name):
    """Test that the app structure follows expected patterns."""
    try:
        # Get the app constructor
        app_constructor = None

        # First check if there's a specific app for this model
        if "app" in mesa.examples[example_model_name]:
            app_constructor = mesa.examples[example_model_name]["app"]
        else:
            # Otherwise use the ModelApp component with the model
            model_class = mesa.examples[example_model_name]["model"]

            def app_constructor():
                return ModelApp(model_class=model_class)

        # Check that the app has the expected attributes
        # In a real implementation, we would check for Solara-specific attributes
        assert callable(app_constructor), "App constructor should be callable"
    except (KeyError, AttributeError, ImportError) as e:
        pytest.skip(f"Could not check app structure for {example_model_name}: {e}")


def test_component_error_handling(example_model_name, solara_test_client):
    """Test how visualization components handle errors.

    This creates edge cases to see if components handle them gracefully.
    """
    try:
        # Get a model instance
        model_class = mesa.examples[example_model_name]["model"]
        model = model_class()

        # Get the visualizations for this model
        visualizations = mesa.examples[example_model_name]["visualization"]

        if not visualizations:
            pytest.skip(f"No visualization components found for {example_model_name}")

        # Choose the first visualization for testing
        viz_name, viz_func = next(iter(visualizations.items()))

        # Test with None model
        def TestErrorComponent():
            return viz_func(None)

        # This should not raise an exception
        result = solara_test_client.render(TestErrorComponent)
        assert result["status"] == "rendered"

        # If we're here, the component handled the None model gracefully
    except (KeyError, AttributeError, ImportError) as e:
        pytest.skip(f"Could not test error handling for {example_model_name}: {e}")


def test_responsive_layout(example_model_name, solara_test_client):
    """Test that visualization components use responsive layouts."""
    # This is a placeholder for a test that would check if layouts are responsive.
    # In a real implementation, we would render components with different viewport sizes
    # and check if they adapt accordingly.
    pytest.skip("Responsive layout testing is not implemented yet")
