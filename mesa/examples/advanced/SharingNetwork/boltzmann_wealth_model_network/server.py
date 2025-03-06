from mesa_old.visualization.ModularVisualization import ModularServer
from mesa_old.visualization.UserParam import UserSettableParameter
from mesa_old.visualization.modules import ChartModule
from mesa_old.visualization.modules import NetworkModule
from mesa_old.visualization.modules import BarChartModule
from .model import DefenderNetworkModel


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
            else f"Agent:{agents[0].unique_id} \nAltruism:{agents[0].altruism} \nWealth:{agents[0].wealth} \nContr:{agents[0].contribution}",
        }
        for (node_id, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {"id": edge_id, "source": source, "target": target, "color": "#000000"}
        for edge_id, (source, target) in enumerate(G.edges)
    ]

    return portrayal


grid = NetworkModule(network_portrayal, 500, 500, library="sigma")
chart = ChartModule(
    [{"Label": "Contribution", "Color": "Black"}], data_collector_name="datacollector"
)
agent_bar = BarChartModule(
    [{"Label": "wealth", "Color": "Red"}],
    scope="agent",
    sorting="ascending",
    sort_by="wealth",
)
chart2 = ChartModule(
    [{"Label": "Average Gain", "Color": "Blue"}], data_collector_name="datacollector2"
)

model_params = {
    "num_groups": UserSettableParameter(
        "slider",
        "Number of groups",
        7,
        2,
        10,
        1,
        description="Choose how many groups to include in the model",
    ),
    "num_members": UserSettableParameter(
        "slider",
        "Number of nodes",
        6,
        3,
        12,
        1,
        description="Choose how many nodes to include in the model, with at "
        "least the same number of agents",
    ),
    "prob_add_friend": UserSettableParameter(
        "slider",
        "percentage",
        0.5,
        0.3,
        0.9,
        0.1,
        description="Choose likelihood to add friends",
    ),
}

server = ModularServer(
    DefenderNetworkModel, [grid, chart], "Money Model", model_params
)
server.port = 8521
