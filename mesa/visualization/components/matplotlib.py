from collections import defaultdict

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


# matplotlib scatter does not allow for multiple shapes in one call
def _split_and_scatter(space_ax, portray_data) -> None:
    cmap = portray_data.pop("cmap", None)

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

                # TODO: break into helper functions for readability
                # apply color map if not RGB(A) format or color string (mimicking default matplotlib behavior)
                if not (
                    isinstance(color, str)  # str format
                    or (
                        (len(color) == 3 or len(color) == 4)  # RGB(A)
                        and (
                            all(
                                # all floats, valid RGB(A)
                                isinstance(c, (int, float)) and 0 <= c <= 1
                                for c in color
                            )
                        )
                    )
                ):
                    color = get_cmap(cmap[i])(color)

                grouped_data[marker][key].append(color)
            elif key != "cmap":  # do nothing special, don't pass on color maps
                grouped_data[marker][key].append(portray_data[key][i])

    print(grouped_data)


def _draw_grid(space, space_ax, agent_portrayal):
    def portray(g):

        default_values = {
            "size": (180 / max(g.width, g.height)) ** 2,
        }

        out = {}

        # used to initialize lists for alignment purposes
        num_agents = len(space._agent_to_index)

        for i, agent in enumerate(space._agent_to_index):
            data = agent_portrayal(agent)

            for key, value in data.items():
                if key not in out:
                    # initialize list
                    out[key] = [default_values.get(key, default=None)] * num_agents
                out[key][i] = value

        return out

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

        default_values = {
            "size": 20,
        }

        out = {}

        # used to initialize lists for alignment purposes
        num_agents = len(space._agent_to_index)

        for i, agent in enumerate(space._agent_to_index):
            data = agent_portrayal(agent)

            for key, value in data.items():
                if key not in out:
                    # initialize list
                    out[key] = [default_values.get(key, default=None)] * num_agents
                out[key][i] = value

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
