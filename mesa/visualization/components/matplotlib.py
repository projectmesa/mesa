"""Matplotlib based solara components for visualization MESA spaces and plots."""

import itertools
import math
import warnings
from collections.abc import Callable

from typing import Dict

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import solara
from matplotlib.cm import ScalarMappable
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgba
from matplotlib.figure import Figure
from matplotlib.patches import RegularPolygon

import mesa
from mesa.experimental.cell_space import (
    OrthogonalMooreGrid,
    OrthogonalVonNeumannGrid,
    VoronoiGrid,
)
from mesa.space import (
    ContinuousSpace,
    HexMultiGrid,
    HexSingleGrid,
    MultiGrid,
    NetworkGrid,
    PropertyLayer,
    SingleGrid,
)
from mesa.visualization.utils import update_counter

OrthogonalGrid = SingleGrid | MultiGrid | OrthogonalMooreGrid | OrthogonalVonNeumannGrid
HexGrid = HexSingleGrid | HexMultiGrid | mesa.experimental.cell_space.HexGrid
Network = NetworkGrid | mesa.experimental.cell_space.Network


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
    """Create a Matplotlib-based space visualization component."""
    update_counter.get()

    space = getattr(model, "grid", None)
    if space is None:
        space = getattr(model, "space", None)

    fig = Figure()
    ax = fig.subplots(111)

    # https://stackoverflow.com/questions/67524641/convert-multiple-isinstance-checks-to-structural-pattern-matching
    match space:
        case mesa.space._Grid() | OrthogonalMooreGrid() | OrthogonalVonNeumannGrid():
            draw_orthogonal_grid(space, agent_portrayal, ax)
        case HexSingleGrid() | HexMultiGrid() | mesa.experimental.cell_space.HexGrid():
            draw_hex_grid(space, agent_portrayal, ax)
        case mesa.space.NetworkGrid() | mesa.experimental.cell_space.Network():
            draw_network(space, agent_portrayal, ax)
        case mesa.space.ContinuousSpace():
            draw_continuous_space(space, agent_portrayal, ax)
        case VoronoiGrid():
            draw_voroinoi_grid(space, agent_portrayal, ax)

    if propertylayer_portrayal:
        draw_property_layers(space, propertylayer_portrayal, model, ax)

    solara.FigureMatplotlib(
        fig, format="png", bbox_inches="tight", dependencies=dependencies
    )


def draw_property_layers(space, propertylayer_portrayal: Dict[str:Dict], ax):
    """Draw PropertyLayers on the given axes.

    Args:
        space (mesa.space._Grid): The space containing the PropertyLayers.
        propertylayer_portrayal (dict): the key is the name of the layer, the value is a dict with
                                        fields specifying how the layer is to be portrayed
        model (mesa.Model): The model instance.
        ax (matplotlib.axes.Axes): The axes to draw on.

    Notes:
        valid fields in in the inner dict of propertylayer_portrayal are "alpha", "vmin", "vmax", "color" or "colormap", and "colorbar"
        so you can do `{"some_layer":{"colormap":'viridis', 'alpha':.25, "colorbar":False}}`

    """
    try:
        # old style spaces
        property_layers = space.properties
    except AttributeError:
        # new style spaces
        property_layers = space.property_layers

    for layer_name, portrayal in propertylayer_portrayal.items():
        layer = property_layers.get(layer_name, None)
        if not isinstance(layer, PropertyLayer):
            continue

        data = layer.data.astype(float) if layer.data.dtype == bool else layer.data
        width, height = data.shape if space is None else (space.width, space.height)

        if space and data.shape != (width, height):
            warnings.warn(
                f"Layer {layer_name} dimensions ({data.shape}) do not match space dimensions ({width}, {height}).",
                UserWarning,
                stacklevel=2,
            )

        # Get portrayal properties, or use defaults
        alpha = portrayal.get("alpha", 1)
        vmin = portrayal.get("vmin", np.min(data))
        vmax = portrayal.get("vmax", np.max(data))
        colorbar = portrayal.get("colorbar", True)

        # Draw the layer
        if "color" in portrayal:
            rgba_color = to_rgba(portrayal["color"])
            normalized_data = (data - vmin) / (vmax - vmin)
            rgba_data = np.full((*data.shape, 4), rgba_color)
            rgba_data[..., 3] *= normalized_data * alpha
            rgba_data = np.clip(rgba_data, 0, 1)
            cmap = LinearSegmentedColormap.from_list(
                layer_name, [(0, 0, 0, 0), (*rgba_color[:3], alpha)]
            )
            im = ax.imshow(
                rgba_data.transpose(1, 0, 2),
                origin="lower",
            )
            if colorbar:
                norm = Normalize(vmin=vmin, vmax=vmax)
                sm = ScalarMappable(norm=norm, cmap=cmap)
                sm.set_array([])
                ax.figure.colorbar(sm, ax=ax, orientation="vertical")

        elif "colormap" in portrayal:
            cmap = portrayal.get("colormap", "viridis")
            if isinstance(cmap, list):
                cmap = LinearSegmentedColormap.from_list(layer_name, cmap)
            im = ax.imshow(
                data.T,
                cmap=cmap,
                alpha=alpha,
                vmin=vmin,
                vmax=vmax,
                origin="lower",
            )
            if colorbar:
                plt.colorbar(im, ax=ax, label=layer_name)
        else:
            raise ValueError(
                f"PropertyLayer {layer_name} portrayal must include 'color' or 'colormap'."
            )


def collect_agent_data(
    space: OrthogonalGrid | HexGrid | Network | ContinuousSpace,
    agent_portrayal: Callable,
    c_default="tab:blue",
    marker_default="o",
    s_default=25,
):
    """Collect the plotting data for all agents in the space.

    Args:
        space: The space containing the Agents.
        agent_portrayal: A callable that is called with the agent and returns a dict
        loc: a boolean indicating whether to gather agent x, y data or not
        c_default: default color
        marker_default: default marker
        s_default: default size

    Notes:
        agent portray dict is limited to s (size of marker), c (color of marker, and marker (marker style)
        see `Matplotlib`_.


    .. _Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html

    """
    arguments = {"loc": [], "s": [], "c": [], "marker": []}
    for agent in space.agents:
        portray = agent_portrayal(agent)
        loc = agent.pos
        if loc is None:
            loc = agent.cell.coordinate

        arguments["loc"].append(loc)
        arguments["s"].append(portray.get("s", s_default))
        arguments["c"].append(portray.get("c", c_default))
        arguments["marker"].append(portray.get("marker", marker_default))

    return {k: np.asarray(v) for k, v in arguments.items()}


def draw_orthogonal_grid(
    space: OrthogonalGrid,
    agent_portrayal: Callable,
    ax,
):
    """Visualize a orthogonal grid.

    Args:
        space: the space to visualize
        agent_portrayal: a callable that is called with the agent and returns a dict
        ax: a Matplotlib Axes instance

    Returns:
        A Figure and Axes instance

    """
    s_default = (180 / max(space.width, space.height)) ** 2
    arguments = collect_agent_data(space, agent_portrayal, s_default=s_default)

    ax.set_xlim(-0.5, space.width - 0.5)
    ax.set_ylim(-0.5, space.height - 0.5)

    # Draw grid lines
    for x in np.arange(-0.5, space.width - 0.5, 1):
        ax.axvline(x, color="gray", linestyle=":")
    for y in np.arange(-0.5, space.height - 0.5, 1):
        ax.axhline(y, color="gray", linestyle=":")

    _scatter(ax, arguments)


def draw_hex_grid(
    space: HexGrid,
    agent_portrayal: Callable,
    ax,
):
    """Visualize a hex grid.

    Args:
        space: the space to visualize
        agent_portrayal: a callable that is called with the agent and returns a dict
        propertylayer_portrayal: a callable that is called with the agent and returns a dict
        model: a model instance
        ax: a Matplotlib Axes instance

    Returns:
        A Figure and Axes instance

    """
    s_default = (180 / max(space.width, space.height)) ** 2
    arguments = collect_agent_data(space, agent_portrayal, s_default=s_default)

    # give all odd rows an offset in the x direction
    # give all rows an offset in the y direction
    # numbers here are based on a distance of 1 between centers of hexes
    offset = math.sqrt(0.75)

    # logical = np.mod(arguments["y"], 2) == 1
    # arguments["y"] = arguments["y"].astype(float) * offset
    # arguments["x"] = arguments["x"].astype(float)
    # arguments["x"][logical] += 0.5

    loc = arguments["loc"].astype(float)

    logical = np.mod(loc[:, 1], 2) == 0
    loc[:, 0][logical] += 0.5
    loc[:, 1] *= offset
    arguments["loc"] = loc

    ax.set_xlim(-1, space.width + 0.5)
    ax.set_ylim(-offset, space.height * offset)

    _scatter(ax, arguments)

    def setup_hexmesh(
        width,
        height,
    ):
        """Helper function for creating the hexmaesh."""
        # fixme: this should be done once, rather than in each update
        # fixme check coordinate system in hexgrid (see https://www.redblobgames.com/grids/hexagons/#coordinates-offset)

        patches = []
        for x, y in itertools.product(range(width), range(height)):
            if y % 2 == 0:
                x += 0.5  # noqa: PLW2901
            y *= offset  # noqa: PLW2901
            hex = RegularPolygon(
                (x, y),
                numVertices=6,
                radius=math.sqrt(1 / 3),
                orientation=np.radians(120),
            )
            patches.append(hex)
        mesh = PatchCollection(
            patches, edgecolor="k", facecolor=(1, 1, 1, 0), linestyle="dotted", lw=1
        )
        return mesh

    ax.add_collection(
        setup_hexmesh(
            space.width,
            space.height,
        )
    )


def draw_network(space: Network, agent_portrayal: Callable, ax):
    """Visualize a network space.

    Args:
        space: the space to visualize
        agent_portrayal: a callable that is called with the agent and returns a dict
        ax: a Matplotlib Axes instance

    Notes:
        this uses networkx.draw under the hood so agent portrayal fields should match those used there
        i.e., node_size and node_color.


    """
    graph = space.G
    pos = nx.spring_layout(graph, seed=0)
    x, y = list(zip(*pos.values()))
    xmin, xmax = min(x), max(x)
    ymin, ymax = min(y), max(y)

    width = xmax - xmin
    height = ymax - ymin

    s_default = (180 / max(width, height)) ** 2
    arguments = collect_agent_data(space, agent_portrayal, s_default=s_default)

    # this assumes that nodes are identified by an integer
    # which is true for default nx graphs but might user changeable
    pos = np.asarray(list(pos.values()))
    arguments["loc"] = pos[arguments["loc"]]

    ax.set_axis_off()
    ax.set_xlim(xmin=xmin, xmax=xmax)
    ax.set_ylim(ymin=ymin, ymax=ymax)

    _scatter(ax, arguments)
    nx.draw_networkx_edges(graph, pos, ax=ax)


def draw_continuous_space(space: ContinuousSpace, agent_portrayal: Callable, ax):
    """Visualize a continuous space.

    Args:
        space: the space to visualize
        agent_portrayal: a callable that is called with the agent and returns a dict
        ax: a Matplotlib Axes instance

    Returns:
        A Figure and Axes instance

    """
    width = space.x_max - space.x_min
    x_padding = width / 20
    height = space.y_max - space.y_min
    y_padding = height / 20

    s_default = (180 / max(width, height)) ** 2
    arguments = collect_agent_data(space, agent_portrayal, s_default=s_default)

    border_style = "solid" if not space.torus else (0, (5, 10))

    # Set the border of the plot
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
        spine.set_color("black")
        spine.set_linestyle(border_style)

    ax.set_xlim(space.x_min - x_padding, space.x_max + x_padding)
    ax.set_ylim(space.y_min - y_padding, space.y_max + y_padding)

    _scatter(ax, arguments)


def draw_voroinoi_grid(space: VoronoiGrid, agent_portrayal: Callable, ax):
    """Visualize a voronoi grid.

    Args:
        space: the space to visualize
        agent_portrayal: a callable that is called with the agent and returns a dict
        ax: a Matplotlib Axes instance

    Returns:
        A Figure and Axes instance

    """
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

    s_default = (180 / max(width, height)) ** 2
    arguments = collect_agent_data(space, agent_portrayal, s_default=s_default)

    ax.set_xlim(x_min - x_padding, x_max + x_padding)
    ax.set_ylim(y_min - y_padding, y_max + y_padding)

    _scatter(ax, arguments)

    for cell in space.all_cells:
        polygon = cell.properties["polygon"]
        ax.fill(
            *zip(*polygon),
            alpha=min(1, cell.properties[space.cell_coloring_property]),
            c="red",
            zorder=0,
        )  # Plot filled polygon
        ax.plot(*zip(*polygon), color="black")  # Plot polygon edges in black


def _scatter(ax, arguments):
    loc = arguments.pop("loc")

    x = loc[:, 0]
    y = loc[:, 1]
    marker = arguments.pop("marker")

    for mark in np.unique(marker):
        mask = marker == mark
        ax.scatter(
            x[mask], y[mask], marker=mark, **{k: v[mask] for k, v in arguments.items()}
        )


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
        ax.legend(loc="best")
    elif isinstance(measure, list | tuple):
        for m in measure:
            ax.plot(df.loc[:, m], label=m)
        ax.legend(loc="best")
    ax.set_xlabel("Step")
    # Set integer x axis
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    solara.FigureMatplotlib(
        fig, format="png", bbox_inches="tight", dependencies=dependencies
    )
