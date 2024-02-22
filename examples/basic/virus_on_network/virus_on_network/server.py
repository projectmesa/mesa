import math

import mesa

from .model import State, VirusOnNetwork, number_infected


def network_portrayal(G):
    # The model ensures there is always 1 agent per node

    def node_color(agent):
        return {State.INFECTED: "#FF0000", State.SUSCEPTIBLE: "#008000"}.get(
            agent.state, "#808080"
        )

    def edge_color(agent1, agent2):
        if State.RESISTANT in (agent1.state, agent2.state):
            return "#000000"
        return "#e8e8e8"

    def edge_width(agent1, agent2):
        if State.RESISTANT in (agent1.state, agent2.state):
            return 3
        return 2

    def get_agents(source, target):
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    portrayal = {}
    portrayal["nodes"] = [
        {
            "size": 6,
            "color": node_color(agents[0]),
            "tooltip": f"id: {agents[0].unique_id}<br>state: {agents[0].state.name}",
        }
        for (_, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": edge_color(*get_agents(source, target)),
            "width": edge_width(*get_agents(source, target)),
        }
        for (source, target) in G.edges
    ]

    return portrayal


network = mesa.visualization.NetworkModule(
    portrayal_method=network_portrayal,
    canvas_height=500,
    canvas_width=500,
)
chart = mesa.visualization.ChartModule(
    [
        {"Label": "Infected", "Color": "#FF0000"},
        {"Label": "Susceptible", "Color": "#008000"},
        {"Label": "Resistant", "Color": "#808080"},
    ]
)


def get_resistant_susceptible_ratio(model):
    ratio = model.resistant_susceptible_ratio()
    ratio_text = "&infin;" if ratio is math.inf else f"{ratio:.2f}"
    infected_text = str(number_infected(model))

    return "Resistant/Susceptible Ratio: {}<br>Infected Remaining: {}".format(
        ratio_text, infected_text
    )


model_params = {
    "num_nodes": mesa.visualization.Slider(
        name="Number of agents",
        value=10,
        min_value=10,
        max_value=100,
        step=1,
        description="Choose how many agents to include in the model",
    ),
    "avg_node_degree": mesa.visualization.Slider(
        name="Avg Node Degree",
        value=3,
        min_value=3,
        max_value=8,
        step=1,
        description="Avg Node Degree",
    ),
    "initial_outbreak_size": mesa.visualization.Slider(
        name="Initial Outbreak Size",
        value=1,
        min_value=1,
        max_value=10,
        step=1,
        description="Initial Outbreak Size",
    ),
    "virus_spread_chance": mesa.visualization.Slider(
        name="Virus Spread Chance",
        value=0.4,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
        description="Probability that susceptible neighbor will be infected",
    ),
    "virus_check_frequency": mesa.visualization.Slider(
        name="Virus Check Frequency",
        value=0.4,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
        description="Frequency the nodes check whether they are infected by a virus",
    ),
    "recovery_chance": mesa.visualization.Slider(
        name="Recovery Chance",
        value=0.3,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
        description="Probability that the virus will be removed",
    ),
    "gain_resistance_chance": mesa.visualization.Slider(
        name="Gain Resistance Chance",
        value=0.5,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
        description="Probability that a recovered agent will become "
        "resistant to this virus in the future",
    ),
}

server = mesa.visualization.ModularServer(
    model_cls=VirusOnNetwork,
    visualization_elements=[network, get_resistant_susceptible_ratio, chart],
    name="Virus on Network Model",
    model_params=model_params,
)
server.port = 8521
