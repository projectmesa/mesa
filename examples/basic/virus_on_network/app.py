import math

import solara
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from mesa.experimental import JupyterViz, make_text
from virus_on_network.model import State, VirusOnNetwork, number_infected


def agent_portrayal(graph):
    def get_agent(node):
        return graph.nodes[node]["agent"][0]

    edge_width = []
    edge_color = []
    for u, v in graph.edges():
        agent1 = get_agent(u)
        agent2 = get_agent(v)
        w = 2
        ec = "#e8e8e8"
        if State.RESISTANT in (agent1.state, agent2.state):
            w = 3
            ec = "black"
        edge_width.append(w)
        edge_color.append(ec)
    node_color_dict = {
        State.INFECTED: "tab:red",
        State.SUSCEPTIBLE: "tab:green",
        State.RESISTANT: "tab:gray",
    }
    node_color = [node_color_dict[get_agent(node).state] for node in graph.nodes()]
    return {
        "width": edge_width,
        "edge_color": edge_color,
        "node_color": node_color,
    }


def get_resistant_susceptible_ratio(model):
    ratio = model.resistant_susceptible_ratio()
    ratio_text = r"$\infty$" if ratio is math.inf else f"{ratio:.2f}"
    infected_text = str(number_infected(model))

    return "Resistant/Susceptible Ratio: {}<br>Infected Remaining: {}".format(
        ratio_text, infected_text
    )


def make_plot(model):
    # This is for the case when we want to plot multiple measures in 1 figure.
    fig = Figure()
    ax = fig.subplots()
    measures = ["Infected", "Susceptible", "Resistant"]
    colors = ["tab:red", "tab:green", "tab:gray"]
    for i, m in enumerate(measures):
        color = colors[i]
        df = model.datacollector.get_model_vars_dataframe()
        ax.plot(df.loc[:, m], label=m, color=color)
    fig.legend()
    # Set integer x axis
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    solara.FigureMatplotlib(fig)


model_params = {
    "num_nodes": {
        "type": "SliderInt",
        "value": 10,
        "label": "Number of agents",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "avg_node_degree": {
        "type": "SliderInt",
        "value": 3,
        "label": "Avg Node Degree",
        "min": 3,
        "max": 8,
        "step": 1,
    },
    "initial_outbreak_size": {
        "type": "SliderInt",
        "value": 1,
        "label": "Initial Outbreak Size",
        "min": 1,
        "max": 10,
        "step": 1,
    },
    "virus_spread_chance": {
        "type": "SliderFloat",
        "value": 0.4,
        "label": "Virus Spread Chance",
        "min": 0.0,
        "max": 1.0,
        "step": 0.1,
    },
    "virus_check_frequency": {
        "type": "SliderFloat",
        "value": 0.4,
        "label": "Virus Check Frequency",
        "min": 0.0,
        "max": 1.0,
        "step": 0.1,
    },
    "recovery_chance": {
        "type": "SliderFloat",
        "value": 0.3,
        "label": "Recovery Chance",
        "min": 0.0,
        "max": 1.0,
        "step": 0.1,
    },
    "gain_resistance_chance": {
        "type": "SliderFloat",
        "value": 0.5,
        "label": "Gain Resistance Chance",
        "min": 0.0,
        "max": 1.0,
        "step": 0.1,
    },
}

page = JupyterViz(
    VirusOnNetwork,
    model_params,
    measures=[
        make_plot,
        make_text(get_resistant_susceptible_ratio),
    ],
    name="Virus Model",
    agent_portrayal=agent_portrayal,
)
page  # noqa
