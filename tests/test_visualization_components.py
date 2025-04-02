"""tests for mesa visualization components."""

import pytest

from mesa.visualization.components import make_altair_space


def agent_portrayal(agent):
    """Simple portrayal of an agent.

    Args:
        agent (Agent): The agent to portray

    Returns:
        dict: A dictionary with display information
    """
    return {
        "s": 10,
        "c": "tab:blue",
        "marker": "s" if (agent.unique_id % 2) == 0 else "o",
    }


def test_make_altair_space():
    """Test make_altair_space component."""
    # This test simply checks that we can call the function
    # and that it returns a callable
    component = make_altair_space(agent_portrayal)
    assert callable(component), "Component should be callable"


@pytest.mark.parametrize(
    "model_path,portrayal_path",
    [
        (
            "mesa.examples.basic.conways_game_of_life.model.ConwaysGameOfLife",
            "mesa.examples.basic.conways_game_of_life.app.agent_portrayal",
        ),
        (
            "mesa.examples.basic.virus_on_network.model.VirusOnNetwork",
            None,  # No portrayal import needed (removed unused import)
        ),
        (
            "mesa.examples.basic.boltzmann_wealth_model.model.BoltzmannWealth",
            "mesa.examples.basic.boltzmann_wealth_model.app.agent_portrayal",
        ),
    ],
)
def test_example_models_compatible_with_altair(model_path, portrayal_path):
    """Test different example models are compatible with altair space."""
    try:
        # Import the model class
        parts = model_path.split(".")
        module_name = ".".join(parts[:-1])
        class_name = parts[-1]
        # We only need to import the module to verify it exists
        __import__(module_name, fromlist=[class_name])

        # Import portrayal function if path is provided
        if portrayal_path:
            portrayal_parts = portrayal_path.split(".")
            portrayal_module_name = ".".join(portrayal_parts[:-1])
            portrayal_func_name = portrayal_parts[-1]
            portrayal_module = __import__(
                portrayal_module_name, fromlist=[portrayal_func_name]
            )
            agent_portrayal_func = getattr(portrayal_module, portrayal_func_name)
        else:
            # Use the default portrayal if none specified
            agent_portrayal_func = agent_portrayal

        # Create an altair component and verify it works
        component = make_altair_space(agent_portrayal_func)
        assert callable(component), "Component should be callable"
    except ImportError:
        pytest.skip("Example model not available")
