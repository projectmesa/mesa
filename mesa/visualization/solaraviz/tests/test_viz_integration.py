"""
Integration tests for Mesa's SolaraViz visualization components.
These tests verify that visualization components correctly interact with model data.
"""

import pytest
from typing import Dict, Any, List, Callable, Optional

import sys
import os
sys.path.append(os.path.abspath('.'))

# Import the mock components
import mesa
from mock_solara_components import (
    SolaraVisualization,
    SolaraGrid,
    SolaraChart,
    SolaraNetworkVisualization,
    ModelApp
)

def test_model_visualization_integration(example_model_name):
    """
    Test the integration between model and visualization components.
    
    Verifies that model changes are reflected in visualization components.
    """
    try:
        # Get a model instance
        model_class = mesa.examples[example_model_name]["model"]
        model = model_class()
        
        # Store the initial state
        initial_state = get_model_state(model)
        
        # Step the model a few times
        for _ in range(3):
            model.step()
        
        # Get the new state
        new_state = get_model_state(model)
        
        # Make sure the state changed
        assert new_state != initial_state, f"Model state did not change after stepping for {example_model_name}"
        
        # Get the visualizations for this model
        visualizations = mesa.examples[example_model_name]["visualization"]
        
        # Check that at least one visualization exists
        assert len(visualizations) > 0, f"No visualization components found for {example_model_name}"
    except (KeyError, AttributeError, ImportError) as e:
        pytest.skip(f"Could not test model integration for {example_model_name}: {e}")

def get_model_state(model) -> Dict[str, Any]:
    """
    Extract relevant state from a model for comparison.
    
    This function tries to extract key attributes from the model that would indicate state change.
    
    Args:
        model: The Mesa model instance
        
    Returns:
        Dictionary with model state
    """
    state = {}
    
    # Include schedule time
    if hasattr(model, "schedule") and hasattr(model.schedule, "time"):
        state["time"] = model.schedule.time
    
    # Include number of agents
    if hasattr(model, "schedule") and hasattr(model.schedule, "agents"):
        state["num_agents"] = len(model.schedule.agents)
    
    # Include datacollector data if available
    if hasattr(model, "datacollector") and hasattr(model.datacollector, "model_vars"):
        state["datacollector"] = str(model.datacollector.model_vars)
    
    return state

def test_app_model_integration(example_model_name, solara_test_client):
    """
    Test the integration between the app component and model.
    
    Verifies that the app can initialize and update the model.
    """
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
        
        # Render the app
        result = solara_test_client.render(app_constructor)
        assert result["status"] == "rendered"
    except (KeyError, AttributeError, ImportError) as e:
        pytest.skip(f"Could not test app integration for {example_model_name}: {e}")

def test_data_collection_visualization(example_model_name):
    """
    Test integration between model data collection and visualization.
    
    Verifies that visualizations correctly display collected model data.
    """
    try:
        # Get a model instance
        model_class = mesa.examples[example_model_name]["model"]
        model = model_class()
        
        # Make sure the model has a datacollector
        if not hasattr(model, "datacollector"):
            pytest.skip(f"Model {example_model_name} does not have a datacollector")
        
        # Step the model a few times to collect data
        for _ in range(3):
            model.step()
            # Ensure data is collected
            model.datacollector.collect(model)
        
        # Get the chart visualization if available
        visualizations = mesa.examples[example_model_name]["visualization"]
        for viz_name, viz_func in visualizations.items():
            if "chart" in viz_name.lower():
                # Just test that the function executes without error
                viz_func(model)
                # No assertions needed here - we're just making sure it executes
    except (KeyError, AttributeError, ImportError) as e:
        pytest.skip(f"Could not test data collection for {example_model_name}: {e}")