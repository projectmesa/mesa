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

    def __init__(self, space: OrthogonalGrid, **kwargs):
        """Initialize the orthogonal space drawer.

        Args:
            space: The orthogonal grid space to draw
            **kwargs: Additional keyword arguments
        """
        self.space = space
        self.s_default = (180 / max(self.space.width, self.space.height)) ** 2

    def draw_matplotlib(self, ax):
        """Draw the orthogonal grid using matplotlib.

        Args:
            ax: Matplotlib axes object to draw on

        Returns:
            The modified axes object
        """
        if ax is None:
            fig, ax = plt.subplots()

        # further styling
        ax.set_xlim(-0.5, self.space.width - 0.5)
        ax.set_ylim(-0.5, self.space.height - 0.5)

        # Draw grid lines
        for x in np.arange(-0.5, self.space.width - 0.5, 1):
            ax.axvline(x, color="gray", linestyle=":")
        for y in np.arange(-0.5, self.space.height - 0.5, 1):
            ax.axhline(y, color="gray", linestyle=":")
        return ax

    def draw_altair(self):
        """Draw the orthogonal grid using Altair.

        Returns:
            Altair chart object
        """
        chart = (
            alt.Chart(pd.DataFrame({"x": [0], "y": [0]}))
            .mark_point(opacity=0)
            .encode(
                x=alt.X("X:Q", scale=alt.Scale(domain=[-0.5, self.space.width - 0.5])),
                y=alt.Y("Y:Q", scale=alt.Scale(domain=[-0.5, self.space.height - 0.5])),
            )
            .properties(width=450, height=350)
        )
        return chart


class HexSpaceDrawer:
    """Drawer for hexagonal grid spaces."""

    def __init__(self, space: HexGrid, **kwargs):
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

    def draw_matplotlib(self, ax):
        """Draw the hexagonal grid using matplotlib.

        Args:
            ax: Matplotlib axes object to draw on

        Returns:
            The modified axes object
        """
        if ax is None:
            fig, ax = plt.subplots()

        ax.set_xlim(-2 * self.x_padding, self.x_max + self.x_padding)
        ax.set_ylim(-2 * self.y_padding, self.y_max + self.y_padding)

        def setup_hexmesh():
            """Helper function for creating the hexmesh with unique edges."""
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

            return LineCollection(
                edges, linestyle=":", color="black", linewidth=1, alpha=1
            )

        ax.add_collection(setup_hexmesh())
        return ax

    def draw_altair(self):
        """Draw the hexagonal grid using Altair.

        Raises:
            NotImplementedError: Altair drawing not yet implemented for hex grids
        """
        raise NotImplementedError("Altair drawing not implemented for HexSpaceDrawer.")


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
        self.s_default = (180 / max(self.space.width, self.space.height)) ** 2
        self.layout_alg = layout_alg
        self.layout_kwargs = layout_kwargs if layout_kwargs is not None else {"seed": 0}

        self.pos = None

    def draw_matplotlib(self, ax):
        """Draw the network using matplotlib.

        Args:
            ax: Matplotlib axes object to draw on

        Returns:
            The modified axes object
        """
        if ax is None:
            fig, ax = plt.subplots()

        # gather locations for nodes in network
        graph = self.space.G
        self.pos = self.layout_alg(graph, **self.layout_kwargs)
        x, y = list(zip(*self.pos.values()))
        xmin, xmax = min(x), max(x)
        ymin, ymax = min(y), max(y)

        width = xmax - xmin
        height = ymax - ymin
        x_padding = width / 20
        y_padding = height / 20

        # further styling
        ax.set_axis_off()
        ax.set_xlim(xmin=xmin - x_padding, xmax=xmax + x_padding)
        ax.set_ylim(ymin=ymin - y_padding, ymax=ymax + y_padding)

        # draw the nodes
        # FIXME: we need to draw the empty nodes as well
        edge_collection = nx.draw_networkx_edges(
            graph, self.pos, ax=ax, alpha=0.5, style="--"
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
