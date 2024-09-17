"""Support for using matplotlib to draw spaces."""

from collections import defaultdict

import networkx as nx
import solara
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

import mesa
from mesa.experimental.cell_space import VoronoiGrid


@solara.component
def SpaceMatplotlib(model, agent_portrayal, dependencies: list[any] | None = None):
    """A component for rendering a space using Matplotlib.

    Args:
        model: a model instance
        agent_portrayal: a specification of how to portray an agent.
        dependencies: list of dependencies.

    """
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
    elif isinstance(space, VoronoiGrid):
        _draw_voronoi(space, space_ax, agent_portrayal)
    else:
        _draw_grid(space, space_ax, agent_portrayal)
    solara.FigureMatplotlib(space_fig, format="png", dependencies=dependencies)


# matplotlib scatter does not allow for multiple shapes in one call
def _split_and_scatter(portray_data, space_ax):
    grouped_data = defaultdict(lambda: {"x": [], "y": [], "s": [], "c": []})

    # Extract data from the dictionary
    x = portray_data["x"]
    y = portray_data["y"]
    s = portray_data["s"]
    c = portray_data["c"]
    m = portray_data["m"]

    if not (len(x) == len(y) == len(s) == len(c) == len(m)):
        raise ValueError(
            "Length mismatch in portrayal data lists: "
            f"x: {len(x)}, y: {len(y)}, size: {len(s)}, "
            f"color: {len(c)}, marker: {len(m)}"
        )

    # Group the data by marker
    for i in range(len(x)):
        marker = m[i]
        grouped_data[marker]["x"].append(x[i])
        grouped_data[marker]["y"].append(y[i])
        grouped_data[marker]["s"].append(s[i])
        grouped_data[marker]["c"].append(c[i])

    # Plot each group with the same marker
    for marker, data in grouped_data.items():
        space_ax.scatter(data["x"], data["y"], s=data["s"], c=data["c"], marker=marker)


def _draw_grid(space, space_ax, agent_portrayal):
    def portray(g):
        x = []
        y = []
        s = []  # size
        c = []  # color
        m = []  # shape
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

                    # This is the default value for the marker size, which auto-scales
                    # according to the grid area.
                    default_size = (180 / max(g.width, g.height)) ** 2
                    # establishing a default prevents misalignment if some agents are not given size, color, etc.
                    size = data.get("size", default_size)
                    s.append(size)
                    color = data.get("color", "tab:blue")
                    c.append(color)
                    mark = data.get("shape", "o")
                    m.append(mark)
        out = {"x": x, "y": y, "s": s, "c": c, "m": m}
        return out

    space_ax.set_xlim(-1, space.width)
    space_ax.set_ylim(-1, space.height)
    _split_and_scatter(portray(space), space_ax)


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
        m = []  # shape
        for agent in space._agent_to_index:
            data = agent_portrayal(agent)
            _x, _y = agent.pos
            x.append(_x)
            y.append(_y)

            # This is matplotlib's default marker size
            default_size = 20
            # establishing a default prevents misalignment if some agents are not given size, color, etc.
            size = data.get("size", default_size)
            s.append(size)
            color = data.get("color", "tab:blue")
            c.append(color)
            mark = data.get("shape", "o")
            m.append(mark)
        out = {"x": x, "y": y, "s": s, "c": c, "m": m}
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
    _split_and_scatter(portray(space), space_ax)


def _draw_voronoi(space, space_ax, agent_portrayal):
    def portray(g):
        x = []
        y = []
        s = []  # size
        c = []  # color

        for cell in g.all_cells:
            for agent in cell.agents:
                data = agent_portrayal(agent)
                x.append(cell.coordinate[0])
                y.append(cell.coordinate[1])
                if "size" in data:
                    s.append(data["size"])
                if "color" in data:
                    c.append(data["color"])
        out = {"x": x, "y": y}
        # This is the default value for the marker size, which auto-scales
        # according to the grid area.
        out["s"] = s
        if len(c) > 0:
            out["c"] = c

        return out

    x_list = [i[0] for i in space.centroids_coordinates]
    y_list = [i[1] for i in space.centroids_coordinates]
    x_max = max(x_list)
    x_min = min(x_list)
    y_max = max(y_list)
    y_min = min(y_list)

    width = x_max - x_min
    x_padding = width / 20
    height = y_max - y_min
    y_padding = height / 20
    space_ax.set_xlim(x_min - x_padding, x_max + x_padding)
    space_ax.set_ylim(y_min - y_padding, y_max + y_padding)
    space_ax.scatter(**portray(space))

    for cell in space.all_cells:
        polygon = cell.properties["polygon"]
        space_ax.fill(
            *zip(*polygon),
            alpha=min(1, cell.properties[space.cell_coloring_property]),
            c="red",
        )  # Plot filled polygon
        space_ax.plot(*zip(*polygon), color="black")  # Plot polygon edges in red


@solara.component
def PlotMatplotlib(model, measure, dependencies: list[any] | None = None):
    """A solara component for creating a matplotlib figure.

    Args:
        model: Model instance
        measure: measure to plot
        dependencies: list of additional dependencies

    """
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
    elif isinstance(measure, list | tuple):
        for m in measure:
            ax.plot(df.loc[:, m], label=m)
        fig.legend()
    # Set integer x axis
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    solara.FigureMatplotlib(fig, dependencies=dependencies)
