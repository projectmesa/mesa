"""Matplotlib based solara components for visualization MESA spaces and plots."""

import warnings

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import solara
from matplotlib.colors import LinearSegmentedColormap, to_rgba
from matplotlib.figure import Figure

import mesa
from mesa.experimental.cell_space import VoronoiGrid
from mesa.space import PropertyLayer
from mesa.visualization.utils import update_counter


def make_space_matplotlib(agent_portrayal=None, propertylayer_portrayal=None):
    """Create a Matplotlib-based space visualization component.

    Args:
        agent_portrayal (function): Function to portray agents
        propertylayer_portrayal (dict): Dictionary of PropertyLayer portrayal specifications

    Returns:
        function: A function that creates a SpaceMatplotlib component
    """
    if agent_portrayal is None:

        def agent_portrayal(a):
            return {"id": a.unique_id}

    def MakeSpaceMatplotlib(model):
        return SpaceMatplotlib(model, agent_portrayal, propertylayer_portrayal)

    return MakeSpaceMatplotlib


@solara.component
def SpaceMatplotlib(
    model,
    agent_portrayal,
    propertylayer_portrayal,
    dependencies: list[any] | None = None,
):
    update_counter.get()
    space_fig = Figure()
    space_ax = space_fig.subplots()
    space = getattr(model, "grid", None)
    if space is None:
        space = getattr(model, "space", None)

    if isinstance(space, mesa.space._Grid):
        _draw_grid(space, space_ax, agent_portrayal, propertylayer_portrayal, model)
    elif isinstance(space, mesa.space.ContinuousSpace):
        _draw_continuous_space(
            space, space_ax, agent_portrayal, propertylayer_portrayal, model
        )
    elif isinstance(space, mesa.space.NetworkGrid):
        _draw_network_grid(space, space_ax, agent_portrayal)
    elif isinstance(space, VoronoiGrid):
        _draw_voronoi(space, space_ax, agent_portrayal, propertylayer_portrayal, model)
    elif space is None and propertylayer_portrayal:
        draw_property_layers(space_ax, space, propertylayer_portrayal, model)

    solara.FigureMatplotlib(space_fig, format="png", dependencies=dependencies)


def draw_property_layers(ax, space, propertylayer_portrayal, model):
    """Draw PropertyLayers on the given axes.

    Args:
        ax (matplotlib.axes.Axes): The axes to draw on.
        space (mesa.space._Grid): The space containing the PropertyLayers.
        propertylayer_portrayal (dict): Dictionary of PropertyLayer portrayal specifications.
        model (mesa.Model): The model instance.
    """
    for layer_name, portrayal in propertylayer_portrayal.items():
        layer = getattr(model, layer_name, None)
        if layer is None or not isinstance(layer, PropertyLayer):
            continue

        alpha = portrayal.get("alpha", 0.5)

        # Convert boolean arrays to float
        data = layer.data.astype(float) if layer.data.dtype == bool else layer.data

        vmin = portrayal.get("vmin", np.min(data))
        vmax = portrayal.get("vmax", np.max(data))

        if space is not None:
            # Check if the dimensions align
            if data.shape != (space.width, space.height):
                warnings.warn(
                    f"Layer {layer_name} does not have the same dimensions as the space. "
                    "Skipping visualization.",
                    UserWarning,
                )
                continue
            width, height = space.width, space.height
        else:
            width, height = data.shape

        if "color" in portrayal:
            # Use color with alpha scaling
            color = portrayal["color"]
            rgba_color = to_rgba(color)  # Convert any color format to RGBA
            normalized_data = (data - vmin) / (vmax - vmin)
            rgba_data = np.zeros((*data.shape, 4))
            rgba_data[..., :3] = rgba_color[:3]  # RGB channels
            rgba_data[..., 3] = normalized_data * alpha * rgba_color[3]  # Alpha channel
            im = ax.imshow(
                rgba_data.transpose(1, 0, 2),  # Transpose to (height, width, 4)
                extent=(0, width, 0, height),
                origin="lower",
            )
        else:
            # Use colormap
            cmap = portrayal.get("colormap", "viridis")
            if isinstance(cmap, list):
                cmap = LinearSegmentedColormap.from_list(layer_name, cmap)
            im = ax.imshow(
                data.T,
                cmap=cmap,
                alpha=alpha,
                vmin=vmin,
                vmax=vmax,
                extent=(0, width, 0, height),
                origin="lower",
            )
            plt.colorbar(im, ax=ax, label=layer_name)


def _draw_grid(space, space_ax, agent_portrayal, propertylayer_portrayal, model):
    if propertylayer_portrayal:
        draw_property_layers(space_ax, space, propertylayer_portrayal, model)

    agent_data = _get_agent_data(space, agent_portrayal)

    space_ax.set_xlim(0, space.width)
    space_ax.set_ylim(0, space.height)
    _split_and_scatter(agent_data, space_ax)

    # Draw grid lines
    for x in range(space.width + 1):
        space_ax.axvline(x, color="gray", linestyle=":")
    for y in range(space.height + 1):
        space_ax.axhline(y, color="gray", linestyle=":")


def _get_agent_data(space, agent_portrayal):
    """Helper function to get agent data for visualization."""
    x, y, s, c, m = [], [], [], [], []
    for agents, pos in space.coord_iter():
        if not agents:
            continue
        if not isinstance(agents, list):
            agents = [agents]
        for agent in agents:
            data = agent_portrayal(agent)
            x.append(pos[0] + 0.5)  # Center the agent in the cell
            y.append(pos[1] + 0.5)  # Center the agent in the cell
            default_size = (180 / max(space.width, space.height)) ** 2
            s.append(data.get("size", default_size))
            c.append(data.get("color", "tab:blue"))
            m.append(data.get("shape", "o"))
    return {"x": x, "y": y, "s": s, "c": c, "m": m}


def _split_and_scatter(portray_data, space_ax):
    """Helper function to split and scatter agent data."""
    for marker in set(portray_data["m"]):
        mask = [m == marker for m in portray_data["m"]]
        space_ax.scatter(
            [x for x, show in zip(portray_data["x"], mask) if show],
            [y for y, show in zip(portray_data["y"], mask) if show],
            s=[s for s, show in zip(portray_data["s"], mask) if show],
            c=[c for c, show in zip(portray_data["c"], mask) if show],
            marker=marker,
        )


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
            size = data.get("size", default_size)
            s.append(size)
            color = data.get("color", "tab:blue")
            c.append(color)
            mark = data.get("shape", "o")
            m.append(mark)
        return {"x": x, "y": y, "s": s, "c": c, "m": m}

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
        space_ax.plot(*zip(*polygon), color="black")  # Plot polygon edges in black


def make_plot_measure(measure: str | dict[str, str] | list[str] | tuple[str]):
    """Create a plotting function for a specified measure.

    Args:
        measure (str | dict[str, str] | list[str] | tuple[str]): Measure(s) to plot.

    Returns:
        function: A function that creates a PlotMatplotlib component.
    """

    def MakePlotMeasure(model):
        return PlotMatplotlib(model, measure)

    return MakePlotMeasure


@solara.component
def PlotMatplotlib(model, measure, dependencies: list[any] | None = None):
    """Create a Matplotlib-based plot for a measure or measures.

    Args:
        model (mesa.Model): The model instance.
        measure (str | dict[str, str] | list[str] | tuple[str]): Measure(s) to plot.
        dependencies (list[any] | None): Optional dependencies for the plot.

    Returns:
        solara.FigureMatplotlib: A component for rendering the plot.
    """
    update_counter.get()
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
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    solara.FigureMatplotlib(fig, dependencies=dependencies)
