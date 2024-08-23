from collections import defaultdict

from matplotlib.colors import Normalize
import networkx as nx
import solara
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from matplotlib.pyplot import get_cmap

import mesa


@solara.component
def SpaceMatplotlib(model, agent_portrayal, dependencies: list[any] | None = None):
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


# used to make non(less?)-breaking change
# this *does* however block the matplotlib 'color' param which is distinct from 'c'.
def _translate_old_keywords(dict):
    key_mapping: dict[str, str] = {"size": "s", "color": "c", "shape": "marker"}
    return {key_mapping.get(key, key): val for (key, val) in dict.items()}


# matplotlib scatter does not allow for multiple shapes in one call
def _split_and_scatter(portray_data, space_ax) -> None:
    cmap = portray_data.pop("cmap", None)
    norm = portray_data.pop("norm", None)

    # enforce marker iterability
    markers = portray_data.pop("marker", ["o"] * len(portray_data["x"]))
    # enforce default color
    # if no 'color' or 'facecolor' or 'c' then default to "tab:blue" color
    if (
        "color" not in portray_data
        and "facecolor" not in portray_data
        and "c" not in portray_data
    ):
        portray_data["color"] = ["tab:blue"] * len(portray_data["x"])

    grouped_data = defaultdict(lambda: {key: [] for key in portray_data})

    for i, marker in enumerate(markers):
        for key in portray_data:
            # apply colormap
            if cmap and key == "c":
                color = portray_data[key][i]
                # apply color map only if the color is numerical representation
                # this ignores RGB(A) and string formats (mimicking default matplotlib behavior)
                if isinstance(color, (int, float)):
                    if norm:
                        if not isinstance(
                            norm[i], Normalize
                        ):  # does not support string norms (yet?)
                            raise TypeError(
                                "'norm' param must be of type Normalize or a subclass."
                            )
                        else:
                            color = norm[i](color)
                    color = get_cmap(cmap[i])(color)
                grouped_data[marker][key].append(color)
            elif (
                key != "cmap" and key != "norm"
            ):  # do nothing special, don't pass on color maps
                grouped_data[marker][key].append(portray_data[key][i])

    for marker, data in grouped_data.items():
        space_ax.scatter(marker=marker, **data)


def _draw_grid(space, space_ax, agent_portrayal):
    def portray(g):

        default_values = {
            "size": (180 / max(g.width, g.height)) ** 2,
        }

        out = {}

        # TODO: find way to avoid iterating twice
        # used to initialize lists for alignment purposes
        num_agents = 0
        for i in range(g.width):
            for j in range(g.height):
                content = g._grid[i][j]
                if not content:
                    continue
                if not hasattr(content, "__iter__"):
                    num_agents += 1
                    continue
                num_agents += len(content)

        index = 0
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
                    data["x"] = i
                    data["y"] = j

                    for key, value in data.items():
                        if key not in out:
                            # initialize list
                            out[key] = [default_values.get(key, None)] * num_agents
                        out[key][index] = value
                    index += 1

        return _translate_old_keywords(out)

    space_ax.set_xlim(-1, space.width)
    space_ax.set_ylim(-1, space.height)

    # portray and scatter the agents in the space
    _split_and_scatter(portray(space), space_ax)


# draws using networkx's matplotlib integration
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

        # TODO: look into if more default values are needed
        #   especially relating to 'color', 'facecolor', and 'c' params &
        #   interactions w/ the current implementation of _split_and_scatter
        default_values = {
            "s": 20,
        }

        out = {}

        # used to initialize lists for alignment purposes
        num_agents = len(space._agent_to_index)

        for i, agent in enumerate(space._agent_to_index):
            data = agent_portrayal(agent)
            data["x"], data["y"] = agent.pos

            for key, value in data.items():
                if key not in out:
                    # initialize list
                    out[key] = [default_values.get(key, default=None)] * num_agents
                out[key][i] = value

        return _translate_old_keywords(out)

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

    # portray and scatter the agents in the space
    _split_and_scatter(portray(space), space_ax)


@solara.component
def PlotMatplotlib(model, measure, dependencies: list[any] | None = None):
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
