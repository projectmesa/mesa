import warnings

import numpy as np
from backends import AltairBackend, MatplotlibBackend
from matplotlib.axes import Axes
from solara import Literal
from space_drawers import (
    ContinuousSpaceDrawer,
    HexSpaceDrawer,
    NetworkSpaceDrawer,
    OrthogonalSpaceDrawer,
    VoronoiSpaceDrawer,
)

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

# Define type hints for space types
OrthogonalGrid = SingleGrid | MultiGrid | OrthogonalMooreGrid | OrthogonalVonNeumannGrid
HexGrid = HexSingleGrid | HexMultiGrid | mesa.discrete_space.HexGrid
Network = NetworkGrid | mesa.discrete_space.Network


class SpaceRenderer:
    """Renders Mesa spaces using different backends."""

    def __init__(
        self,
        model,
        backend: Literal["matplotlib", "altair"] | None = "matplotlib",
        **kwargs,
    ):
        self.space = getattr(model, "grid", getattr(model, "space", None))

        self.space_drawer = self._get_space_drawer()
        self.space_mesh = None
        self.agent_mesh = None
        self.propertylayer_mesh = None

        self.backend = backend

        if backend == "matplotlib":
            self.backend_renderer = MatplotlibBackend(
                self.space_drawer,
                [self.space_mesh, self.agent_mesh, self.propertylayer_mesh],
            )
        elif backend == "altair":
            self.backend_renderer = AltairBackend(
                self.space_drawer,
                [self.space_mesh, self.agent_mesh, self.propertylayer_mesh],
            )
        else:
            raise ValueError(f"Unsupported backend: {backend}")

        self.backend_renderer.initialize_canvas(**kwargs)

    def _get_space_drawer(self):
        """Get appropriate space drawer based on space type."""
        if isinstance(self.space, OrthogonalGrid):
            return OrthogonalSpaceDrawer(self.space)
        elif isinstance(self.space, HexGrid):
            return HexSpaceDrawer(self.space)
        elif isinstance(self.space, ContinuousSpace):
            return ContinuousSpaceDrawer(self.space)
        elif isinstance(self.space, VoronoiGrid):
            return VoronoiSpaceDrawer(self.space)
        elif isinstance(self.space, Network):
            return NetworkSpaceDrawer(self.space)
        raise ValueError(
            f"Unsupported space type: {type(self.space).__name__}. "
            "Supported types are OrthogonalGrid, HexGrid, ContinuousSpace, VoronoiGrid, and Network."
        )

    def _map_coordinates(self, arguments):
        """Map agent coordinates to appropriate space coordinates."""
        mapped_arguments = arguments.copy()

        if isinstance(self.space, OrthogonalGrid | VoronoiGrid | ContinuousSpace):
            # Use the coordinates directly for Orthogonal grids, Voronoi grids and Continuous spaces
            mapped_arguments["loc"] = arguments["loc"].astype(float)

        elif isinstance(self.space, HexGrid):
            # Map rectangular coordinates to hexagonal grid coordinates
            loc = arguments["loc"].astype(float)
            if loc.size > 0:
                # Calculate hexagon centers
                loc[:, 0] = loc[:, 0] * self.space_drawer.x_spacing + (
                    (loc[:, 1] - 1) % 2
                ) * (self.space_drawer.x_spacing / 2)
                loc[:, 1] = loc[:, 1] * self.space_drawer.y_spacing
            mapped_arguments["loc"] = loc

        elif isinstance(self.space, Network):
            # Map coordinates for Network spaces
            loc = arguments["loc"].astype(float)
            pos = np.asarray(list(self.space_drawer.pos.values()))
            # For network only both x and y contains the correct coordinates
            # use one of them
            x = loc[:, 0]
            if x is None:
                x = loc[:, 1]

            # Ensure x is an integer index for the position mapping
            x = x.astype(int)

            mapped_arguments["loc"] = pos[x - 1]  # Adjust for 1-based indexing

        return mapped_arguments

    def draw_structure(self, ax: Axes | None = None, **kwargs):
        self.space_kwargs = kwargs

        if self.backend == "altair":
            # Altair backend does not use Axes
            ax = None
        ax = ax or self.canvas
        self.space_mesh = self.backend_renderer.draw_structure(ax, **self.space_kwargs)
        return self.space_mesh

    def draw_agents(self, agent_portrayal, ax: Axes | None = None, **kwargs):
        self.agent_portrayal = agent_portrayal
        ax = ax or self.canvas
        self.agent_kwargs = kwargs
        arguments = self.backend_renderer._collect_agent_data(
            self.space, agent_portrayal
        )
        arguments = self._map_coordinates(arguments)

        if self.backend == "altair":
            # Altair backend does not use Axes
            ax = None

        self.agent_mesh = self.backend_renderer.draw_agents(
            ax, arguments, **self.agent_kwargs
        )
        return self.agent_mesh

    def draw_propertylayer(self, propertylayer_portrayal, ax: Axes | None = None):
        # Import here to avoid circular imports
        from mesa.visualization.components import PropertyLayerStyle

        ax = ax if ax is not None else self.canvas

        def _dict_to_callable(portrayal_dict):
            """Convert legacy dict portrayal to callable."""

            def style_callable(layer_object):
                layer_name = layer_object.name
                params = portrayal_dict.get(layer_name)

                warnings.warn(
                    "Dict propertylayer_portrayal is deprecated. "
                    "Use a callable returning PropertyLayerStyle instead.",
                    PendingDeprecationWarning,
                    stacklevel=2,
                )

                if params is None:
                    return None

                return PropertyLayerStyle(
                    color=params.get("color"),
                    colormap=params.get("colormap"),
                    alpha=params.get("alpha", PropertyLayerStyle.alpha),
                    vmin=params.get("vmin"),
                    vmax=params.get("vmax"),
                    colorbar=params.get("colorbar", PropertyLayerStyle.colorbar),
                )

            return style_callable

        # Get property layers
        try:
            # old style spaces
            property_layers = self.space.properties
        except AttributeError:
            # new style spaces
            property_layers = self.space._mesa_property_layers

        # Convert portrayal to callable if needed
        if isinstance(propertylayer_portrayal, dict):
            self.propertylayer_portrayal = _dict_to_callable(propertylayer_portrayal)
        else:
            self.propertylayer_portrayal = propertylayer_portrayal

        if len(property_layers) < 2:
            warnings.warn(
                "No property layers found in the space. "
                "Ensure that the space has property layers defined.",
                UserWarning,
                stacklevel=2,
            )
            return ax, None

        self.propertylayer_mesh = self.backend_renderer.draw_propertylayer(
            self.space, property_layers, self.propertylayer_portrayal, ax
        )
        return self.propertylayer_mesh

    def render(self, agent_portrayal=None, propertylayer_portrayal=None, **kwargs):
        return self.backend_renderer.render(
            self.space, agent_portrayal, propertylayer_portrayal, **kwargs
        )

    @property
    def canvas(self):
        """Return the current canvas object."""
        return self.backend_renderer.canvas

    def clear_meshes(self):
        self.backend_renderer.clear_meshes()
