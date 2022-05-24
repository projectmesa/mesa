import mesa

from .model import BoltzmannWealthModelNetwork


def network_portrayal(G):
    # The model ensures there is 0 or 1 agent per node

    portrayal = dict()
    portrayal["nodes"] = [
        {
            "id": node_id,
            "size": 3 if agents else 1,
            "color": "#CC0000" if not agents or agents[0].wealth == 0 else "#007959",
            "label": None
            if not agents
            else f"Agent:{agents[0].unique_id} Wealth:{agents[0].wealth}",
        }
        for (node_id, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {"id": edge_id, "source": source, "target": target, "color": "#000000"}
        for edge_id, (source, target) in enumerate(G.edges)
    ]

    return portrayal


grid = mesa.visualization.NetworkModule(network_portrayal, 500, 500)
chart = mesa.visualization.ChartModule(
    [{"Label": "Gini", "Color": "Black"}], data_collector_name="datacollector"
)

model_params = {
    "num_agents": mesa.visualization.Slider(
        "Number of agents",
        7,
        2,
        10,
        1,
        description="Choose how many agents to include in the model",
    ),
    "num_nodes": mesa.visualization.Slider(
        "Number of nodes",
        10,
        3,
        12,
        1,
        description="Choose how many nodes to include in the model, with at "
        "least the same number of agents",
    ),
}

server = mesa.visualization.ModularServer(
    BoltzmannWealthModelNetwork, [grid, chart], "Money Model", model_params
)
server.port = 8521
