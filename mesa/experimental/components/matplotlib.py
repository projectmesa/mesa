from typing import Optional

import networkx as nx
import solara
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

import mesa


@solara.component
def SpaceMatplotlib(model, agent_portrayal, dependencies: Optional[list[any]] = None):
    space_fig = Figure()
    space_ax = space_fig.subplots()
    space = getattr(model, "grid", None)
    if space is None:
        # Sometimes the space is defined as model.space instead of model.grid
        space = model.space
    if isinstance(space, mesa.space.NetworkGrid):
        _draw_network_grid(space, space_ax, agent_portrayal)
    elif isinstance(space, mesa.space.ContinuousSpace):
        _draw_continuous_space(space, space_ax, agent_portrayal)
    else:
        _draw_grid(space, space_ax, agent_portrayal)
    solara.FigureMatplotlib(space_fig, format="png", dependencies=dependencies)


def _draw_grid(space, space_ax, agent_portrayal):
    def portray(g):
        x = []
        y = []
        s = []  # size
        c = []  # color
        for i in range(g.width):
            for j in range(g.height):
                content = g._grid[i][j]
                if not content:
                    continue
                if not hasattr(content, "__iter__"):
                    # Is a single grid
                    content = [content]
                for agent in content:
                    data = agent_portrayal(agent)
                    x.append(i)
                    y.append(j)
                    if "size" in data:
                        s.append(data["size"])
                    if "color" in data:
                        c.append(data["color"])
        out = {"x": x, "y": y}
        # This is the default value for the marker size, which auto-scales
        # according to the grid area.
        out["s"] = (180 / max(g.width, g.height)) ** 2
        if len(s) > 0:
            out["s"] = s
        if len(c) > 0:
            out["c"] = c
        return out

    space_ax.set_xlim(-1, space.width)
    space_ax.set_ylim(-1, space.height)
    space_ax.scatter(**portray(space))


def _draw_network_grid(space, space_ax, agent_portrayal):
    graph = space.G
    pos = nx.spring_layout(graph, seed=0)
    nx.draw(
        graph,
        ax=space_ax,
        pos=pos,
        **agent_portrayal(graph),
    )


def _draw_continuous_space(space, space_ax, agent_portrayal):
    def portray(space):
        x = []
        y = []
        s = []  # size
        c = []  # color
        for agent in space._agent_to_index:
            data = agent_portrayal(agent)
            _x, _y = agent.pos
            x.append(_x)
            y.append(_y)
            if "size" in data:
                s.append(data["size"])
            if "color" in data:
                c.append(data["color"])
        out = {"x": x, "y": y}
        if len(s) > 0:
            out["s"] = s
        if len(c) > 0:
            out["c"] = c
        return out

    # Determine border style based on space.torus
    border_style = "solid" if not space.torus else (0, (5, 10))

    # Set the border of the plot
    for spine in space_ax.spines.values():
        spine.set_linewidth(1.5)
        spine.set_color("black")
        spine.set_linestyle(border_style)

    width = space.x_max - space.x_min
    x_padding = width / 20
    height = space.y_max - space.y_min
    y_padding = height / 20
    space_ax.set_xlim(space.x_min - x_padding, space.x_max + x_padding)
    space_ax.set_ylim(space.y_min - y_padding, space.y_max + y_padding)

    # Portray and scatter the agents in the space
    space_ax.scatter(**portray(space))


@solara.component
def PlotMatplotlib(model, measure, dependencies: Optional[list[any]] = None):
    fig = Figure()
    ax = fig.subplots()
    df = model.datacollector.get_model_vars_dataframe()
    if isinstance(measure, str):
        ax.plot(df.loc[:, measure])
        ax.set_ylabel(measure)
    elif isinstance(measure, dict):
        for m, color in measure.items():
            ax.plot(df.loc[:, m], label=m, color=color)
        fig.legend()
    elif isinstance(measure, (list, tuple)):
        for m in measure:
            ax.plot(df.loc[:, m], label=m)
        fig.legend()
    # Set integer x axis
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    solara.FigureMatplotlib(fig, dependencies=dependencies)
