"""Mesa visualization space drawers for different spatial models.

This module provides drawer classes for visualizing different types of spatial
models in Mesa, including orthogonal grids, hexagonal grids, networks,
continuous spaces, and Voronoi grids.
"""

import itertools
from itertools import pairwise

import altair as alt
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Polygon

import mesa
from mesa.discrete_space import (
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
    SingleGrid,
)

OrthogonalGrid = SingleGrid | MultiGrid | OrthogonalMooreGrid | OrthogonalVonNeumannGrid
HexGrid = HexSingleGrid | HexMultiGrid | mesa.discrete_space.HexGrid
Network = NetworkGrid | mesa.discrete_space.Network


class OrthogonalSpaceDrawer:
    """Drawer for orthogonal grid spaces (SingleGrid, MultiGrid, Moore, VonNeumann)."""

    def __init__(self, space: OrthogonalGrid):
        """Initialize the orthogonal space drawer.

        Args:
            space: The orthogonal grid space to draw
            **kwargs: Additional keyword arguments
        """
        self.space = space
        self.s_default = (180 / max(self.space.width, self.space.height)) ** 2

    def draw_matplotlib(self, ax, **space_kwargs):
        """Draw the orthogonal grid using matplotlib.

        Args:
            ax: Matplotlib axes object to draw on
            space_kwargs: Additional keyword arguments for styling

        Returns:
            The modified axes object
        """
        fig_kwargs = {
            "figsize": space_kwargs.pop("figsize", (8, 8)),
            "dpi": space_kwargs.pop("dpi", 100),
        }

        if ax is None:
            fig, ax = plt.subplots(**fig_kwargs)

        # gridline styling kwargs
        line_kwargs = {
            "color": space_kwargs.pop("color", "gray"),
            "linestyle": space_kwargs.pop("linestyle", ":"),
            "linewidth": space_kwargs.pop("linewidth", 1),
            "alpha": space_kwargs.pop("alpha", 1),
        }

        # Remaining kwargs for title, xlabel, ylabel, aspect, etc.
        ax.set(**space_kwargs)

        ax.set_xlim(-0.5, self.space.width - 0.5)
        ax.set_ylim(-0.5, self.space.height - 0.5)

        # Draw grid lines
        for x in np.arange(-0.5, self.space.width - 0.5, 1):
            ax.axvline(x, **line_kwargs)
        for y in np.arange(-0.5, self.space.height - 0.5, 1):
            ax.axhline(y, **line_kwargs)

        return ax

    def draw_altair(self, **chart_kwargs):
        """Draw the orthogonal grid using Altair.

        Args:
            chart_kwargs: Additional keyword arguments for styling the chart

        Returns:
            Altair chart object
        """
        # for axis and grid styling
        axis_kwargs = {
            "xlabel": chart_kwargs.pop("xlabel", "X"),
            "ylabel": chart_kwargs.pop("ylabel", "Y"),
            "grid_color": chart_kwargs.pop("grid_color", "lightgray"),
            "grid_dash": chart_kwargs.pop("grid_dash", [2, 2]),
            "grid_width": chart_kwargs.pop("grid_width", 1),
            "grid_opacity": chart_kwargs.pop("grid_opacity", 1),
        }

        # for chart properties
        chart_props = {
            "width": chart_kwargs.pop("width", 450),
            "height": chart_kwargs.pop("height", 350),
            "title": chart_kwargs.pop("title", ""),
        }
        chart_props.update(chart_kwargs)

        chart = (
            alt.Chart(pd.DataFrame([{}]))
            .mark_point(opacity=0)
            .encode(
                x=alt.X(
                    "X:Q",
                    scale=alt.Scale(domain=[-0.5, self.space.width - 0.5], nice=False),
                    title=axis_kwargs["xlabel"],
                    axis=alt.Axis(
                        gridColor=axis_kwargs["grid_color"],
                        gridDash=axis_kwargs["grid_dash"],
                        gridWidth=axis_kwargs["grid_width"],
                        gridOpacity=axis_kwargs["grid_opacity"],
                    ),
                ),
                y=alt.Y(
                    "Y:Q",
                    scale=alt.Scale(domain=[-0.5, self.space.height - 0.5], nice=False),
                    title=axis_kwargs["ylabel"],
                    axis=alt.Axis(
                        gridColor=axis_kwargs["grid_color"],
                        gridDash=axis_kwargs["grid_dash"],
                        gridWidth=axis_kwargs["grid_width"],
                        gridOpacity=axis_kwargs["grid_opacity"],
                    ),
                ),
            )
            .properties(**chart_props)
        )
        return chart


class HexSpaceDrawer:
    """Drawer for hexagonal grid spaces."""

    def __init__(self, space: HexGrid):
        """Initialize the hexagonal space drawer.

        Args:
            space: The hexagonal grid space to draw
            **kwargs: Additional keyword arguments
        """
        self.space = space
        self.s_default = (180 / max(self.space.width, self.space.height)) ** 2
        self.size = 1.0
        self.x_spacing = np.sqrt(3) * self.size
        self.y_spacing = 1.5 * self.size

        self.x_max = self.space.width * self.x_spacing + (self.space.height % 2) * (
            self.x_spacing / 2
        )
        self.y_max = self.space.height * self.y_spacing

        self.x_padding = (
            self.size * np.sqrt(3) / 2
        )  # Distance from center to rightmost point of hexagon
        self.y_padding = self.size

        self.hexagons = self._get_hexmesh(self.space.width, self.space.height)

    def _get_hexmesh(
        self, width: int, height: int, size: float = 1.0
    ) -> list[tuple[float, float]]:
        """Generate hexagon vertices for the mesh. Yields list of vertex coordinates for each hexagon."""

        # Helper function for getting the vertices of a hexagon given the center and size
        def _get_hex_vertices(
            center_x: float, center_y: float, size: float = 1.0
        ) -> list[tuple[float, float]]:
            """Get vertices for a hexagon centered at (center_x, center_y)."""
            vertices = [
                (center_x, center_y + size),  # top
                (center_x + size * np.sqrt(3) / 2, center_y + size / 2),  # top right
                (center_x + size * np.sqrt(3) / 2, center_y - size / 2),  # bottom right
                (center_x, center_y - size),  # bottom
                (center_x - size * np.sqrt(3) / 2, center_y - size / 2),  # bottom left
                (center_x - size * np.sqrt(3) / 2, center_y + size / 2),  # top left
            ]
            return vertices

        x_spacing = np.sqrt(3) * size
        y_spacing = 1.5 * size
        hexagons = []

        for row, col in itertools.product(range(height), range(width)):
            # Calculate center position with offset for even rows
            x = col * x_spacing + (row % 2 == 0) * (x_spacing / 2)
            y = row * y_spacing
            hexagons.append(_get_hex_vertices(x, y, size))

        return hexagons

    def draw_matplotlib(self, ax, **space_kwargs):
        """Draw the hexagonal grid using matplotlib.

        Args:
            ax: Matplotlib axes object to draw on
            space_kwargs: Additional keyword arguments for styling

        Returns:
            The modified axes object
        """
        fig_kwargs = {
            "figsize": space_kwargs.pop("figsize", (8, 8)),
            "dpi": space_kwargs.pop("dpi", 100),
        }

        if ax is None:
            fig, ax = plt.subplots(**fig_kwargs)

        line_kwargs = {
            "color": space_kwargs.pop("color", "black"),
            "linestyle": space_kwargs.pop("linestyle", ":"),
            "linewidth": space_kwargs.pop("linewidth", 1),
            "alpha": space_kwargs.pop("alpha", 0.8),
        }

        ax.set(**space_kwargs)

        ax.set_xlim(-2 * self.x_padding, self.x_max + self.x_padding)
        ax.set_ylim(-2 * self.y_padding, self.y_max + self.y_padding)

        edges = set()
        # Generate edges for each hexagon
        for vertices in self.hexagons:
            # Edge logic, connecting each vertex to the next
            for v1, v2 in pairwise([*vertices, vertices[0]]):
                # Sort vertices to ensure consistent edge representation and avoid duplicates.
                edge = tuple(sorted([tuple(np.round(v1, 6)), tuple(np.round(v2, 6))]))
                edges.add(edge)

        ax.add_collection(LineCollection(edges, **line_kwargs))
        return ax

    def draw_altair(self, **chart_kwargs):
        """Draw the hexagonal grid using Altair.

        Args:
            chart_kwargs: Additional keyword arguments for styling the chart

        Returns:
            Altair chart object representing the hexagonal grid.
        """
        edge_data = []
        if self.hexagons:
            edges = set()
            # Generate edges for each hexagon
            for vertices in self.hexagons:
                # Edge logic, connecting each vertex to the next
                for v1, v2 in pairwise([*vertices, vertices[0]]):
                    # Sort vertices to ensure consistent edge representation and avoid duplicates.
                    edge = tuple(
                        sorted([tuple(np.round(v1, 6)), tuple(np.round(v2, 6))])
                    )
                    edges.add(edge)

            # Prepare data for Altair: each edge needs two points (start and end)
            for i, edge_tuple in enumerate(edges):
                p1, p2 = edge_tuple
                edge_data.append(
                    {"edge_id": i, "point_order": 0, "x": p1[0], "y": p1[1]}
                )
                edge_data.append(
                    {"edge_id": i, "point_order": 1, "x": p2[0], "y": p2[1]}
                )

        # Create DataFrame from the edge data, empty if no hexagons.
        source = (
            pd.DataFrame(edge_data)
            if edge_data
            else pd.DataFrame({"edge_id": [], "point_order": [], "x": [], "y": []})
        )

        mark_props = {
            "color": chart_kwargs.pop("color", "black"),
            "strokeDash": chart_kwargs.pop("strokeDash", [2, 2]),
            "strokeWidth": chart_kwargs.pop("strokeWidth", 1),
            "opacity": chart_kwargs.pop("opacity", 0.8),
        }

        chart_props = {
            "width": chart_kwargs.pop("width", 450),
            "height": chart_kwargs.pop("height", 350),
            "title": chart_kwargs.pop("title", ""),
        }
        chart_props.update(chart_kwargs)

        # Setting domain for x and y axes with padding
        domain_x = (-2 * self.x_padding, self.x_max + self.x_padding)
        domain_y = (-2 * self.y_padding, self.y_max + self.y_padding)

        chart = (
            alt.Chart(source)
            .mark_line(**mark_props)
            .encode(
                x=alt.X(
                    "x:Q",
                    title=chart_kwargs.pop("xlabel", "X"),
                    scale=alt.Scale(domain=domain_x, zero=False),
                ),
                y=alt.Y(
                    "y:Q",
                    title=chart_kwargs.pop("ylabel", "Y"),
                    scale=alt.Scale(domain=domain_y, zero=False),
                ),
                detail="edge_id:N",
                order="point_order:Q",
            )
            .properties(**chart_props)
        )

        return chart


class NetworkSpaceDrawer:
    """Drawer for network-based spaces."""

    def __init__(
        self, space: Network, layout_alg=nx.spring_layout, layout_kwargs=None, **kwargs
    ):
        """Initialize the network space drawer.

        Args:
            space: The network space to draw
            layout_alg: NetworkX layout algorithm to use
            layout_kwargs: Keyword arguments for the layout algorithm
            **kwargs: Additional keyword arguments
        """
        self.space = space

        self.layout_alg = layout_alg
        self.layout_kwargs = layout_kwargs if layout_kwargs is not None else {"seed": 0}

        # gather locations for nodes in network
        self.graph = self.space.G
        self.pos = self.layout_alg(self.graph, **self.layout_kwargs)

        x, y = list(zip(*self.pos.values()))
        self.xmin, self.xmax = min(x), max(x)
        self.ymin, self.ymax = min(y), max(y)

        self.width = self.xmax - self.xmin
        self.height = self.ymax - self.ymin

        self.s_default = (180 / max(self.width, self.height)) ** 2

    def draw_matplotlib(self, ax):
        """Draw the network using matplotlib.

        Args:
            ax: Matplotlib axes object to draw on

        Returns:
            The modified axes object
        """
        if ax is None:
            fig, ax = plt.subplots()

        x_padding = self.width / 20
        y_padding = self.height / 20

        # further styling
        ax.set_axis_off()
        ax.set_xlim(xmin=self.xmin - x_padding, xmax=self.xmax + x_padding)
        ax.set_ylim(ymin=self.ymin - y_padding, ymax=self.ymax + y_padding)

        # draw the nodes
        # FIXME: we need to draw the empty nodes as well
        edge_collection = nx.draw_networkx_edges(
            self.graph, self.pos, ax=ax, alpha=0.5, style="--"
        )
        edge_collection.set_zorder(0)

        return ax

    def draw_altair(self):
        """Draw the network using Altair.

        Raises:
            NotImplementedError: Altair drawing not yet implemented for networks
        """
        raise NotImplementedError(
            "Altair drawing not implemented for NetworkSpaceDrawer."
        )


class ContinuousSpaceDrawer:
    """Drawer for continuous spaces."""

    def __init__(self, space: ContinuousSpace, **kwargs):
        """Initialize the continuous space drawer.

        Args:
            space: The continuous space to draw
            **kwargs: Additional keyword arguments
        """
        self.space = space

        self.width = self.space.x_max - self.space.x_min
        self.height = self.space.y_max - self.space.y_min
        self.s_default = (180 / max(self.width, self.height)) ** 2

    def draw_matplotlib(self, ax):
        """Draw the continuous space using matplotlib.

        Args:
            ax: Matplotlib axes object to draw on

        Returns:
            The modified axes object
        """
        if ax is None:
            fig, ax = plt.subplots()

        x_padding = self.width / 20
        y_padding = self.height / 20

        border_style = "solid" if not self.space.torus else (0, (5, 10))
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
            spine.set_color("black")
            spine.set_linestyle(border_style)

        ax.set_xlim(self.space.x_min - x_padding, self.space.x_max + x_padding)
        ax.set_ylim(self.space.y_min - y_padding, self.space.y_max + y_padding)

        return ax

    def draw_altair(self):
        """Draw the continuous space using Altair.

        Raises:
            NotImplementedError: Altair drawing not yet implemented for continuous spaces
        """
        raise NotImplementedError(
            "Altair drawing not implemented for ContinuousSpaceDrawer."
        )


class VoronoiSpaceDrawer:
    """Drawer for Voronoi diagram spaces."""

    def __init__(self, space: VoronoiGrid, **kwargs):
        """Initialize the Voronoi space drawer.

        Args:
            space: The Voronoi grid space to draw
            **kwargs: Additional keyword arguments
        """
        self.space = space

        x_list = [i[0] for i in self.space.centroids_coordinates]
        y_list = [i[1] for i in self.space.centroids_coordinates]
        self.x_max, self.x_min = max(x_list), min(x_list)
        self.y_max, self.y_min = max(y_list), min(y_list)

        self.width = self.x_max - self.x_min
        self.height = self.y_max - self.y_min
        self.s_default = (180 / max(self.width, self.height)) ** 2

    def draw_matplotlib(self, ax):
        """Draw the Voronoi diagram using matplotlib.

        Args:
            ax: Matplotlib axes object to draw on

        Returns:
            The modified axes object
        """
        if ax is None:
            fig, ax = plt.subplots()

        x_padding = self.width / 20
        y_padding = self.height / 20

        ax.set_xlim(self.x_min - x_padding, self.x_max + x_padding)
        ax.set_ylim(self.y_min - y_padding, self.y_max + y_padding)

        def setup_voroinoimesh(cells):
            patches = []
            for cell in cells:
                patch = Polygon(cell.properties["polygon"])
                patches.append(patch)
            mesh = PatchCollection(
                patches, edgecolor="k", facecolor=(1, 1, 1, 0), linestyle="dotted", lw=1
            )
            return mesh

        ax.add_collection(setup_voroinoimesh(self.space.all_cells.cells))
        return ax

    def draw_altair(self):
        """Draw the Voronoi diagram using Altair.

        Raises:
            NotImplementedError: Altair drawing not yet implemented for Voronoi grids
        """
        raise NotImplementedError(
            "Altair drawing not implemented for VoronoiSpaceDrawer."
        )
