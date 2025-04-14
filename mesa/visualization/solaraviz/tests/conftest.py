"""Configuration and fixtures for pytest that are shared across test files for
Mesa's SolaraViz visualization components.
"""

import functools
import os
import signal

# Import the mock Mesa module for testing
import sys

import pytest

sys.path.append(os.path.abspath("."))
import mesa


# Mock Solara test client
class MockSolaraTestClient:
    """Mock implementation of a Solara test client for testing"""

    def __init__(self):
        self.rendered_components = []

    def render(self, component, *args, **kwargs):
        """Render a component and record it"""
        self.rendered_components.append((component, args, kwargs))
        return {
            "status": "rendered",
            "component": component.__name__
            if hasattr(component, "__name__")
            else str(component),
        }

    def clear(self):
        """Clear rendered components"""
        self.rendered_components = []


def timeout_decorator(seconds):
    """Decorator to enforce a timeout for a function"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutError(
                    f"Function {func.__name__} timed out after {seconds} seconds"
                )

            # Set the timeout handler
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
            finally:
                # Reset the alarm
                signal.alarm(0)

            return result

        return wrapper

    return decorator


@pytest.fixture(scope="session")
def solara_test_client():
    """Create a Solara test client that can be used to test Solara applications.
    This is a session-scoped fixture to avoid creating multiple clients.
    """
    client = MockSolaraTestClient()
    yield client
    # Clean up if needed


@pytest.fixture(params=list(mesa.examples.keys()))
def example_model_name(request):
    """Fixture that provides each example model name to the test function."""
    return request.param


@pytest.fixture
def example_model(example_model_name):
    """Fixture to load and instantiate an example model by name."""
    try:
        model_class = mesa.examples[example_model_name]["model"]
        return model_class()
    except (KeyError, ImportError) as e:
        pytest.skip(f"Could not load model for {example_model_name}: {e}")


@pytest.fixture
def example_app(example_model_name):
    """Fixture to load the Solara app for a given example model."""
    try:
        # First check if there's a specific app for this model
        if "app" in mesa.examples[example_model_name]:
            return mesa.examples[example_model_name]["app"]

        # Otherwise create a generic app using the model
        model_class = mesa.examples[example_model_name]["model"]

        # Import here to avoid circular imports
        from mock_solara_components import ModelApp

        def app():
            return ModelApp(model_class=model_class)

        return app
    except (KeyError, ImportError) as e:
        pytest.skip(f"Could not load app for {example_model_name}: {e}")
