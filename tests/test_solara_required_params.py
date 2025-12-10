"""Minimal test case for SolaraViz required parameter validation.

This reproduces the issue where models with required parameters (no default values)
should work with SolaraViz when those parameters are provided via model_params.
"""
import solara

from mesa import Model
from mesa.visualization.solara_viz import SolaraViz


class MoneyModel(Model):
    """Model with required parameters (no defaults)."""

    def __init__(self, n: int, width: int, height: int, seed=None):
        """Initialize the model with required parameters."""
        super().__init__(seed=seed)
        self.n = n
        self.width = width
        self.height = height


def test_required_params_work_with_model_params():
    """SolaraViz should work with models that have required parameters."""
    # Define the parameters to pass to the model
    model_params = {
        "n": 10,
        "width": 10,
        "height": 10,
    }

    # Create initial model instance
    model = MoneyModel(n=10, width=10, height=10)

    # This should NOT raise ValueError about missing parameters
    # The parameters are provided via model_params
    try:
        solara.render(
            SolaraViz(model, model_params=model_params),
            handle_error=False
        )
        print("✓ Test passed: SolaraViz accepts required parameters via model_params")
    except ValueError as e:
        if "Missing required model parameter" in str(e):
            print(f"✗ Test FAILED: {e}")
            raise
        else:
            raise


if __name__ == "__main__":
    test_required_params_work_with_model_params()
