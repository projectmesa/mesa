import matplotlib.pyplot as plt
import pandas as pd
import solara

from mesa.examples.basic.warehouse.model import WarehouseModel
from mesa.visualization import SolaraViz
from mesa.visualization.utils import update_counter

# Constants
LOADING_DOCKS = [(0, 0, 0), (0, 2, 0), (0, 4, 0), (0, 6, 0), (0, 8, 0)]
AXIS_LIMITS = {"x": (0, 22), "y": (0, 20), "z": (0, 5)}

model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
}


def prepare_agent_data(model, agent_type, agent_label):
    """
    Prepare data for agents of a specific type.

    Args:
        model: The WarehouseModel instance.
        agent_type: The type of agent (e.g., "InventoryAgent", "RobotAgent").
        agent_label: The label for the agent type.

    Returns:
        A list of dictionaries containing agent coordinates and type.
    """
    return [
        {
            "x": agent.cell.coordinate[0],
            "y": agent.cell.coordinate[1],
            "z": agent.cell.coordinate[2],
            "type": agent_label,
        }
        for agent in model.agents_by_type[agent_type]
    ]


@solara.component
def plot_warehouse(model):
    """
    Visualize the warehouse model in a 3D scatter plot.

    Args:
        model: The WarehouseModel instance.
    """
    update_counter.get()

    # Prepare data for inventory and robot agents
    inventory_data = prepare_agent_data(model, "InventoryAgent", "Inventory")
    robot_data = prepare_agent_data(model, "RobotAgent", "Robot")

    # Combine data into a single DataFrame
    data = pd.DataFrame(inventory_data + robot_data)

    # Create Matplotlib 3D scatter plot
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    # Highlight loading dock cells
    for i, dock in enumerate(LOADING_DOCKS):
        ax.scatter(
            dock[0],
            dock[1],
            dock[2],
            c="yellow",
            label="Loading Dock"
            if i == 0
            else None,  # Add label only to the first dock
            s=300,
            marker="o",
        )

    # Plot inventory agents
    inventory = data[data["type"] == "Inventory"]
    ax.scatter(
        inventory["x"],
        inventory["y"],
        inventory["z"],
        c="blue",
        label="Inventory",
        s=100,
        marker="s",
    )

    # Plot robot agents
    robots = data[data["type"] == "Robot"]
    ax.scatter(robots["x"], robots["y"], robots["z"], c="red", label="Robot", s=200)

    # Set labels, title, and legend
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Warehouse Visualization")
    ax.legend()

    # Configure plot appearance
    ax.grid(False)
    ax.set_xlim(*AXIS_LIMITS["x"])
    ax.set_ylim(*AXIS_LIMITS["y"])
    ax.set_zlim(*AXIS_LIMITS["z"])
    ax.axis("off")

    # Render the plot in Solara
    solara.FigureMatplotlib(fig)


# Create initial model instance
model = WarehouseModel()

# Create the SolaraViz page
page = SolaraViz(
    model,
    components=[plot_warehouse],
    model_params=model_params,
    name="Pseudo-Warehouse Model",
)

page  # noqa
