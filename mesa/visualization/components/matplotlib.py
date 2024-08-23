from collections import defaultdict

from matplotlib.pylab import norm
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
import networkx as nx
import solara
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
def _translate_old_keywords(data):
    """
    Translates old keyword names in the given dictionary to the new names.
    """
    key_mapping = {"size": "s", "color": "c", "shape": "marker"}
    return {key_mapping.get(key, key): val for (key, val) in data.items()}


def _apply_color_map(color, cmap=None, norm=None, vmin=None, vmax=None):
    """
    Given parameters for manual colormap application, applies color map
    according to default implementation in matplotlib
    """
    if not cmap:  # if no colormap is provided, return original color
        return color
    color_map = plt.get_cmap(cmap)
    if norm:  # check if norm is provided and apply it
        if not isinstance(norm, Normalize):
            raise TypeError(
                "'norm' must be an instance of Normalize or its subclasses."
            )
        return color_map(norm(color))
    if not (vmin == None or vmax == None):  # check for custom norm params
        new_norm = Normalize(vmin, vmax)
        return color_map(new_norm(color))
    try:
        return color_map(color)
    except Exception as e:
        raise ValueError("Color mapping failed due to invalid arguments") from e


# matplotlib scatter does not allow for multiple shapes in one call
def _split_and_scatter(portray_data: dict, space_ax) -> None:
    # if any of the following params are passed into portray(), this is true
    cmap_exists = portray_data.pop("cmap", None)
    norm_exists = portray_data.pop("norm", None)
    vmin_exists = portray_data.pop("vmin", None)
    vmax_exists = portray_data.pop("vmax", None)

    # enforce marker iterability
    markers = portray_data.pop("marker", ["o"] * len(portray_data["x"]))
    # enforce default color
    if (  # if no 'color' or 'facecolor' or 'c' then default to "tab:blue" color
        "color" not in portray_data
        and "facecolor" not in portray_data
        and "c" not in portray_data
    ):
        portray_data["color"] = ["tab:blue"] * len(portray_data["x"])

    grouped_data = defaultdict(lambda: {key: [] for key in portray_data})

    for i, marker in enumerate(markers):

        for key in portray_data:
            if key == "c":  # apply colormap if possible
                # prepare arguments
                cmap = cmap_exists[i] if cmap_exists else None
                norm = norm_exists[i] if norm_exists else None
                vmin = vmin_exists[i] if vmin_exists else None
                vmax = vmax_exists[i] if vmax_exists else None
                # apply colormap with prepared arguments
                portray_data["c"][i] = _apply_color_map(
                    portray_data["c"][i], cmap, norm, vmin, vmax
                )

            grouped_data[marker][key].append(portray_data[key][i])

    for marker, data in grouped_data.items():
        space_ax.scatter(marker=marker, **data)


def _draw_grid(space, space_ax, agent_portrayal):
    def portray(g):

        default_values = {
            "size": (180 / max(g.width, g.height)) ** 2,
        }

        out = {}
        num_agents = 0  # TODO: find way to avoid iterating twice
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
        default_values = {"s": 20}
        out = {}
        num_agents = len(space._agent_to_index)

        for i, agent in enumerate(space._agent_to_index):
            data = agent_portrayal(agent)
            data["x"], data["y"] = agent.pos

            for key, value in data.items():
                if key not in out:  # initialize list
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
