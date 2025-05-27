"""Utility functions for testing Mesa's SolaraViz visualization components."""

import os
import sys
import time
from collections.abc import Callable
from typing import Any

sys.path.append(os.path.abspath("."))

# Import the mock components
import mesa


def import_model_and_visualization(example_name: str) -> tuple[Any | None, Any | None]:
    """Import the model and visualization modules for a given example.

    Args:
        example_name: Name of the example model

    Returns:
        Tuple of (model_module, viz_module) or (None, None) if import fails
    """
    try:
        # In the mock environment, we just return the mesa module
        return mesa, mesa
    except ImportError:
        return None, None


def get_solara_components(module) -> list[type]:
    """Extract all Solara component classes from a module.

    Args:
        module: The module to inspect

    Returns:
        List of Solara component classes
    """
    components = []

    # In a real implementation, we would inspect the module for Solara components
    # For now, return a mock list based on visualizations in the examples
    if module == mesa and hasattr(module, "examples"):
        for example_name, example_data in module.examples.items():
            if "visualization" in example_data:
                for viz_name, viz_func in example_data["visualization"].items():
                    components.append(viz_func)

    return components


def get_app_component(example_name: str) -> Callable | None:
    """Get the main app component for an example.

    Args:
        example_name: Name of the example model

    Returns:
        The app component or None if not found
    """
    try:
        # Check if there's a specific app in the examples dictionary
        if example_name in mesa.examples and "app" in mesa.examples[example_name]:
            return mesa.examples[example_name]["app"]

        # Otherwise use the ModelApp component from mock_solara_components
        from mock_solara_components import ModelApp

        if example_name in mesa.examples and "model" in mesa.examples[example_name]:
            model_class = mesa.examples[example_name]["model"]

            def app():
                return ModelApp(model_class=model_class)

            return app
    except (KeyError, ImportError):
        return None


def create_test_model(example_name: str) -> Any | None:
    """Create an instance of the model for the given example.

    Args:
        example_name: Name of the example model

    Returns:
        Instance of the model or None if creation fails
    """
    try:
        if example_name in mesa.examples and "model" in mesa.examples[example_name]:
            model_class = mesa.examples[example_name]["model"]
            return model_class()
    except (KeyError, ImportError):
        return None


def find_visualization_components(example_name: str) -> dict[str, Any]:
    """Find all visualization components for a given example.

    Args:
        example_name: Name of the example model

    Returns:
        Dictionary mapping component names to component objects
    """
    try:
        if (
            example_name in mesa.examples
            and "visualization" in mesa.examples[example_name]
        ):
            return mesa.examples[example_name]["visualization"]
    except (KeyError, ImportError):
        pass

    return {}


def measure_render_time(component, *args, **kwargs) -> float:
    """Measure the time it takes to render a component.

    Args:
        component: The component to render
        *args, **kwargs: Arguments to pass to the component

    Returns:
        Render time in seconds
    """
    start_time = time.time()
    component(*args, **kwargs)
    end_time = time.time()

    return end_time - start_time
