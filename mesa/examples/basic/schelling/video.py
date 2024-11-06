"""Example of using VideoViz with the Schelling model."""

from mesa.examples.basic.schelling.model import Schelling
from mesa.visualization.video_viz import (
    VideoViz,
    make_plot_component,
    make_space_component,
)

# Create model
model = Schelling(10, 10)


def agent_portrayal(agent):
    """Portray agents based on their type."""
    if agent is None:
        return {}

    portrayal = {
        "color": "red" if agent.type == 0 else "blue",
        "size": 25,
        "marker": "s",  # square marker
    }
    return portrayal


# Create visualization with space and some metrics
viz = VideoViz(
    model,
    [
        make_space_component(agent_portrayal=agent_portrayal),
        make_plot_component("happy"),
    ],
    title="Schelling's Segregation Model",
)

# Record simulation
if __name__ == "__main__":
    viz.record(steps=50, filepath="schelling.mp4")
    print("Video saved to: schelling.mp4")
