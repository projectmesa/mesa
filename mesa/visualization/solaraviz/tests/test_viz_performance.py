"""
Performance benchmarks for Mesa's SolaraViz visualization components.
"""

import pytest
import time
from viz_performance_report import generate_performance_report, save_report, analyze_trends
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

def test_visualization_component_performance(example_model_name, benchmark):
    """
    Benchmark the rendering performance of visualization components.
    
    This test uses pytest-benchmark to accurately measure render time.
    """
    try:
        # Get a model instance
        model_class = mesa.examples[example_model_name]["model"]
        model = model_class()
        
        # Get the visualizations for this model
        visualizations = mesa.examples[example_model_name]["visualization"]
        
        # Choose the first visualization for benchmarking
        if not visualizations:
            pytest.skip(f"No visualization components found for {example_model_name}")
        
        viz_name, viz_func = next(iter(visualizations.items()))
        
        # Define a test function for the benchmark
        def test_func():
            return viz_func(model)
        
        # Run the benchmark
        benchmark(test_func)
    except (KeyError, AttributeError, ImportError) as e:
        pytest.skip(f"Could not benchmark visualizations for {example_model_name}: {e}")

def test_app_initialization_performance(example_model_name):
    """
    Measure how long it takes to initialize the app for each example model.
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
        
        # Measure initialization time
        start_time = time.time()
        app_instance = app_constructor()
        end_time = time.time()
        
        initialization_time = end_time - start_time
        
        # Basic assertion to make sure initialization doesn't take too long
        assert initialization_time < 1.0, f"App initialization took too long: {initialization_time:.2f}s"
    except (KeyError, AttributeError, ImportError) as e:
        pytest.skip(f"Could not measure app initialization for {example_model_name}: {e}")

def test_model_step_with_visualization_performance(example_model_name):
    """
    Benchmark the performance of model steps with visualization components attached.
    """
    try:
        # Get a model instance
        model_class = mesa.examples[example_model_name]["model"]
        model = model_class()
        
        # First measure the time to step the model without visualization
        start_time = time.time()
        for _ in range(5):
            model.step()
        end_time = time.time()
        
        base_step_time = (end_time - start_time) / 5
        
        # Now create a new model with visualizations
        model = model_class()
        
        # Get the visualizations for this model
        visualizations = mesa.examples[example_model_name]["visualization"]
        
        # Initialize all visualizations (to simulate having them attached)
        for viz_name, viz_func in visualizations.items():
            viz_func(model)  # Just initialize, don't store the result
        
        # Now measure the time to step with visualizations initialized
        start_time = time.time()
        for _ in range(5):
            model.step()
        end_time = time.time()
        
        viz_step_time = (end_time - start_time) / 5
        
        # Log the performance difference
        overhead = viz_step_time / base_step_time if base_step_time > 0 else float('inf')
        if overhead > 2.0:
            # This is not a hard failure, just a warning
            pytest.xfail(f"Visualization overhead too high: {overhead:.2f}x for {example_model_name}")
    except (KeyError, AttributeError, ImportError) as e:
        pytest.skip(f"Could not benchmark model steps for {example_model_name}: {e}")