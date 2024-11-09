"""Helper functions for drawing mesa spaces with matplotlib.

These functions are used by the provided matplotlib components, but can also be used to quickly visualize
a space with matplotlib for example when creating a mp4 of a movie run or when needing a figure
for a paper.

"""

import contextlib
import itertools
import math
import warnings
from collections.abc import Callable
from typing import Any

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgba
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

OrthogonalGrid = SingleGrid | MultiGrid | OrthogonalMooreGrid | OrthogonalVonNeumannGrid
HexGrid = HexSingleGrid | HexMultiGrid | mesa.experimental.cell_space.HexGrid
Network = NetworkGrid | mesa.experimental.cell_space.Network


def collect_agent_data(
    space: OrthogonalGrid | HexGrid | Network | ContinuousSpace | VoronoiGrid,
    agent_portrayal: Callable,
    color="tab:blue",
    size=25,
    marker="o",
    zorder: int = 1,
):
    """Collect the plotting data for all agents in the space.

    Args:
        space: The space containing the Agents.
        agent_portrayal: A callable that is called with the agent and returns a dict
        color: default color
        size: default size
        marker: default marker
        zorder: default zorder

    agent_portrayal should return a dict, limited to size (size of marker), color (color of marker), zorder (z-order),
    marker (marker style), alpha, linewidths, and edgecolors

    """
    arguments = {
        "s": [],
        "c": [],
        "marker": [],
        "zorder": [],
        "loc": [],
        "alpha": [],
        "edgecolors": [],
        "linewidths": [],
    }

    for agent in space.agents:
        portray = agent_portrayal(agent)
        loc = agent.pos
        if loc is None:
            loc = agent.cell.coordinate

        arguments["loc"].append(loc)
        arguments["s"].append(portray.pop("size", size))
        arguments["c"].append(portray.pop("color", color))
        arguments["marker"].append(portray.pop("marker", marker))
        arguments["zorder"].append(portray.pop("zorder", zorder))

        for entry in ["alpha", "edgecolors", "linewidths"]:
            with contextlib.suppress(KeyError):
                arguments[entry].append(portray.pop(entry))

        if len(portray) > 0:
            ignored_fields = list(portray.keys())
            msg = ", ".join(ignored_fields)
            warnings.warn(
                f"the following fields are not used in agent portrayal and thus ignored: {msg}.",
                stacklevel=2,
            )

    return {k: np.asarray(v) for k, v in arguments.items()}


def draw_space(
    space,
    agent_portrayal: Callable,
    propertylayer_portrayal: dict | None = None,
    ax: Axes | None = None,
    **space_drawing_kwargs,
):
    """Draw a Matplotlib-based visualization of the space.

    Args:
        space: the space of the mesa model
        agent_portrayal: A callable that returns a dict specifying how to show the agent
        propertylayer_portrayal: a dict specifying how to show propertylayer(s)
        ax: the axes upon which to draw the plot
        post_process: a callable called with the Axes instance
        space_drawing_kwargs: any additional keyword arguments to be passed on to the underlying function for drawing the space.

    Returns:
        Returns the Axes object with the plot drawn onto it.

    ``agent_portrayal`` is called with an agent and should return a dict. Valid fields in this dict are "color",
    "size", "marker", "zorder", alpha, linewidths, and edgecolors. Other field are ignored and will result in a user warning.

    """
    if ax is None:
        fig, ax = plt.subplots()

    # https://stackoverflow.com/questions/67524641/convert-multiple-isinstance-checks-to-structural-pattern-matching
    match space:
        # order matters here given the class structure of old-style grid spaces
        case HexSingleGrid() | HexMultiGrid() | mesa.experimental.cell_space.HexGrid():
            draw_hex_grid(space, agent_portrayal, ax=ax, **space_drawing_kwargs)
        case (
            mesa.space.SingleGrid()
            | OrthogonalMooreGrid()
            | OrthogonalVonNeumannGrid()
            | mesa.space.MultiGrid()
        ):
            draw_orthogonal_grid(space, agent_portrayal, ax=ax, **space_drawing_kwargs)
        case mesa.space.NetworkGrid() | mesa.experimental.cell_space.Network():
            draw_network(space, agent_portrayal, ax=ax, **space_drawing_kwargs)
        case mesa.space.ContinuousSpace():
            draw_continuous_space(space, agent_portrayal, ax=ax)
        case VoronoiGrid():
            draw_voronoi_grid(space, agent_portrayal, ax=ax)
        case _:
            raise ValueError(f"Unknown space type: {type(space)}")

    if propertylayer_portrayal:
        draw_property_layers(space, propertylayer_portrayal, ax=ax)

    return ax


def draw_property_layers(
    space, propertylayer_portrayal: dict[str, dict[str, Any]], ax: Axes
):
    """Draw PropertyLayers on the given axes.

    Args:
        space (mesa.space._Grid): The space containing the PropertyLayers.
        propertylayer_portrayal (dict): the key is the name of the layer, the value is a dict with
                                        fields specifying how the layer is to be portrayed
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


def draw_orthogonal_grid(
    space: OrthogonalGrid,
    agent_portrayal: Callable,
    ax: Axes | None = None,
    draw_grid: bool = True,
    **kwargs,
):
    """Visualize a orthogonal grid.

    Args:
        space: the space to visualize
        agent_portrayal: a callable that is called with the agent and returns a dict
        ax: a Matplotlib Axes instance. If none is provided a new figure and ax will be created using plt.subplots
        draw_grid: whether to draw the grid
        kwargs: additional keyword arguments passed to ax.scatter

    Returns:
        Returns the Axes object with the plot drawn onto it.

    ``agent_portrayal`` is called with an agent and should return a dict. Valid fields in this dict are "color",
    "size", "marker", and "zorder". Other field are ignored and will result in a user warning.

    """
    if ax is None:
        fig, ax = plt.subplots()

    # gather agent data
    s_default = (180 / max(space.width, space.height)) ** 2
    arguments = collect_agent_data(space, agent_portrayal, size=s_default)

    # plot the agents
    _scatter(ax, arguments, **kwargs)

    # further styling
    ax.set_xlim(-0.5, space.width - 0.5)
    ax.set_ylim(-0.5, space.height - 0.5)

    if draw_grid:
        # Draw grid lines
        for x in np.arange(-0.5, space.width - 0.5, 1):
            ax.axvline(x, color="gray", linestyle=":")
        for y in np.arange(-0.5, space.height - 0.5, 1):
            ax.axhline(y, color="gray", linestyle=":")

    return ax


def draw_hex_grid(
    space: HexGrid,
    agent_portrayal: Callable,
    ax: Axes | None = None,
    draw_grid: bool = True,
    **kwargs,
):
    """Visualize a hex grid.

    Args:
        space: the space to visualize
        agent_portrayal: a callable that is called with the agent and returns a dict
        ax: a Matplotlib Axes instance. If none is provided a new figure and ax will be created using plt.subplots
        draw_grid: whether to draw the grid
        kwargs: additional keyword arguments passed to ax.scatter

    Returns:
        Returns the Axes object with the plot drawn onto it.

    ``agent_portrayal`` is called with an agent and should return a dict. Valid fields in this dict are "color",
    "size", "marker", and "zorder". Other field are ignored and will result in a user warning.

    """
    if ax is None:
        fig, ax = plt.subplots()

    # gather data
    s_default = (180 / max(space.width, space.height)) ** 2
    arguments = collect_agent_data(space, agent_portrayal, size=s_default)

    # for hexgrids we have to go from logical coordinates to visual coordinates
    # this is a bit messy.

    # give all even rows an offset in the x direction
    # give all rows an offset in the y direction

    # numbers here are based on a distance of 1 between centers of hexes
    offset = math.sqrt(0.75)

    loc = arguments["loc"].astype(float)

    logical = np.mod(loc[:, 1], 2) == 0
    loc[:, 0][logical] += 0.5
    loc[:, 1] *= offset
    arguments["loc"] = loc

    # plot the agents
    _scatter(ax, arguments, **kwargs)

    # further styling and adding of grid
    ax.set_xlim(-1, space.width + 0.5)
    ax.set_ylim(-offset, space.height * offset)

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

    if draw_grid:
        # add grid
        ax.add_collection(
            setup_hexmesh(
                space.width,
                space.height,
            )
        )
    return ax


def draw_network(
    space: Network,
    agent_portrayal: Callable,
    ax: Axes | None = None,
    draw_grid: bool = True,
    layout_alg=nx.spring_layout,
    layout_kwargs=None,
    **kwargs,
):
    """Visualize a network space.

    Args:
        space: the space to visualize
        agent_portrayal: a callable that is called with the agent and returns a dict
        ax: a Matplotlib Axes instance. If none is provided a new figure and ax will be created using plt.subplots
        draw_grid: whether to draw the grid
        layout_alg: a networkx layout algorithm or other callable with the same behavior
        layout_kwargs: a dictionary of keyword arguments for the layout algorithm
        kwargs: additional keyword arguments passed to ax.scatter

    Returns:
        Returns the Axes object with the plot drawn onto it.

    ``agent_portrayal`` is called with an agent and should return a dict. Valid fields in this dict are "color",
    "size", "marker", and "zorder". Other field are ignored and will result in a user warning.

    """
    if ax is None:
        fig, ax = plt.subplots()
    if layout_kwargs is None:
        layout_kwargs = {"seed": 0}

    # gather locations for nodes in network
    graph = space.G
    pos = layout_alg(graph, **layout_kwargs)
    x, y = list(zip(*pos.values()))
    xmin, xmax = min(x), max(x)
    ymin, ymax = min(y), max(y)

    width = xmax - xmin
    height = ymax - ymin
    x_padding = width / 20
    y_padding = height / 20

    # gather agent data
    s_default = (180 / max(width, height)) ** 2
    arguments = collect_agent_data(space, agent_portrayal, size=s_default)

    # this assumes that nodes are identified by an integer
    # which is true for default nx graphs but might user changeable
    pos = np.asarray(list(pos.values()))
    arguments["loc"] = pos[arguments["loc"]]

    # plot the agents
    _scatter(ax, arguments, **kwargs)

    # further styling
    ax.set_axis_off()
    ax.set_xlim(xmin=xmin - x_padding, xmax=xmax + x_padding)
    ax.set_ylim(ymin=ymin - y_padding, ymax=ymax + y_padding)

    if draw_grid:
        # fixme we need to draw the empty nodes as well
        edge_collection = nx.draw_networkx_edges(
            graph, pos, ax=ax, alpha=0.5, style="--"
        )
        edge_collection.set_zorder(0)

    return ax


def draw_continuous_space(
    space: ContinuousSpace, agent_portrayal: Callable, ax: Axes | None = None, **kwargs
):
    """Visualize a continuous space.

    Args:
        space: the space to visualize
        agent_portrayal: a callable that is called with the agent and returns a dict
        ax: a Matplotlib Axes instance. If none is provided a new figure and ax will be created using plt.subplots
        kwargs: additional keyword arguments passed to ax.scatter

    Returns:
        Returns the Axes object with the plot drawn onto it.

    ``agent_portrayal`` is called with an agent and should return a dict. Valid fields in this dict are "color",
    "size", "marker", and "zorder". Other field are ignored and will result in a user warning.

    """
    if ax is None:
        fig, ax = plt.subplots()

    # space related setup
    width = space.x_max - space.x_min
    x_padding = width / 20
    height = space.y_max - space.y_min
    y_padding = height / 20

    # gather agent data
    s_default = (180 / max(width, height)) ** 2
    arguments = collect_agent_data(space, agent_portrayal, size=s_default)

    # plot the agents
    _scatter(ax, arguments, **kwargs)

    # further visual styling
    border_style = "solid" if not space.torus else (0, (5, 10))
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
        spine.set_color("black")
        spine.set_linestyle(border_style)

    ax.set_xlim(space.x_min - x_padding, space.x_max + x_padding)
    ax.set_ylim(space.y_min - y_padding, space.y_max + y_padding)

    return ax


def draw_voronoi_grid(
    space: VoronoiGrid, agent_portrayal: Callable, ax: Axes | None = None, **kwargs
):
    """Visualize a voronoi grid.

    Args:
        space: the space to visualize
        agent_portrayal: a callable that is called with the agent and returns a dict
        ax: a Matplotlib Axes instance. If none is provided a new figure and ax will be created using plt.subplots
        kwargs: additional keyword arguments passed to ax.scatter

    Returns:
        Returns the Axes object with the plot drawn onto it.

    ``agent_portrayal`` is called with an agent and should return a dict. Valid fields in this dict are "color",
    "size", "marker", and "zorder". Other field are ignored and will result in a user warning.

    """
    if ax is None:
        fig, ax = plt.subplots()

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
    arguments = collect_agent_data(space, agent_portrayal, size=s_default)

    ax.set_xlim(x_min - x_padding, x_max + x_padding)
    ax.set_ylim(y_min - y_padding, y_max + y_padding)

    _scatter(ax, arguments, **kwargs)

    for cell in space.all_cells:
        polygon = cell.properties["polygon"]
        ax.fill(
            *zip(*polygon),
            alpha=min(1, cell.properties[space.cell_coloring_property]),
            c="red",
            zorder=0,
        )  # Plot filled polygon
        ax.plot(*zip(*polygon), color="black")  # Plot polygon edges in black

    return ax


def _scatter(ax: Axes, arguments, **kwargs):
    """Helper function for plotting the agents.

    Args:
        ax: a Matplotlib Axes instance
        arguments: the agents specific arguments for platting
        kwargs: additional keyword arguments for ax.scatter

    """
    loc = arguments.pop("loc")

    x = loc[:, 0]
    y = loc[:, 1]
    marker = arguments.pop("marker")
    zorder = arguments.pop("zorder")

    # we check if edgecolor, linewidth, and alpha are specified
    # at the agent level, if not, we remove them from the arguments dict
    # and fallback to the default value in ax.scatter / use what is passed via **kwargs
    for entry in ["edgecolors", "linewidths", "alpha"]:
        if len(arguments[entry]) == 0:
            arguments.pop(entry)
        else:
            if entry in kwargs:
                raise ValueError(
                    f"{entry} is specified in agent portrayal and via plotting kwargs, you can only use one or the other"
                )

    for mark in np.unique(marker):
        mark_mask = marker == mark
        for z_order in np.unique(zorder):
            zorder_mask = z_order == zorder
            logical = mark_mask & zorder_mask

            ax.scatter(
                x[logical],
                y[logical],
                marker=mark,
                zorder=z_order,
                **{k: v[logical] for k, v in arguments.items()},
                **kwargs,
            )
