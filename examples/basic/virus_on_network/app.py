import math

import solara
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from mesa.visualization import Slider, SolaraViz, make_space_matplotlib

from .model import State, VirusOnNetwork, number_infected


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

    return f"Resistant/Susceptible Ratio: {ratio_text}<br>Infected Remaining: {infected_text}"


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
    ax.set_xlabel("Step")
    ax.set_ylabel("Number of Agents")
    return solara.FigureMatplotlib(fig)


model_params = {
    "num_nodes": Slider(
        label="Number of agents",
        value=10,
        min=10,
        max=100,
        step=1,
    ),
    "avg_node_degree": Slider(
        label="Avg Node Degree",
        value=3,
        min=3,
        max=8,
        step=1,
    ),
    "initial_outbreak_size": Slider(
        label="Initial Outbreak Size",
        value=1,
        min=1,
        max=10,
        step=1,
    ),
    "virus_spread_chance": Slider(
        label="Virus Spread Chance",
        value=0.4,
        min=0.0,
        max=1.0,
        step=0.1,
    ),
    "virus_check_frequency": Slider(
        label="Virus Check Frequency",
        value=0.4,
        min=0.0,
        max=1.0,
        step=0.1,
    ),
    "recovery_chance": Slider(
        label="Recovery Chance",
        value=0.3,
        min=0.0,
        max=1.0,
        step=0.1,
    ),
    "gain_resistance_chance": Slider(
        label="Gain Resistance Chance",
        value=0.5,
        min=0.0,
        max=1.0,
        step=0.1,
    ),
}

SpacePlot = make_space_matplotlib(agent_portrayal)

model1 = VirusOnNetwork()

page = SolaraViz(
    model1,
    [
        SpacePlot,
        make_plot,
        # get_resistant_susceptible_ratio,  # TODO: Fix and uncomment
    ],
    model_params=model_params,
    name="Virus Model",
)
page  # noqa
