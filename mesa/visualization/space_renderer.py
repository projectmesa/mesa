"""Mesa Space Rendering Module.

Provides visualization capabilities for Mesa agent-based models with support for
multiple space types (orthogonal grids, hex grids, continuous spaces, etc.) and
rendering backends (matplotlib, altair).

Basic Usage:
    ```python
    from mesa.visualization import SpaceRenderer

    # Initialize renderer with your model
    renderer = SpaceRenderer(model, backend='matplotlib')

    # Draw space structure
    renderer.draw_structure()

    # Draw agents with portrayal function
    renderer.draw_agents(agent_portrayal_function)

    # Draw property layers with portrayal function
    renderer.draw_propertylayer(propertylayer_portrayal_function)

    # Or render everything at once
    renderer.render(agent_portrayal_function)
    ```

Classes:
    SpaceRenderer: Main rendering class for Mesa spaces
"""

import warnings
from collections.abc import Callable
from dataclasses import fields

import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.collections import PolyCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgb, to_rgba

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
from mesa.visualization.space_drawers import (
    ContinuousSpaceDrawer,
    HexSpaceDrawer,
    NetworkSpaceDrawer,
    OrthogonalSpaceDrawer,
    VoronoiSpaceDrawer,
)

# Type aliases
OrthogonalGrid = SingleGrid | MultiGrid | OrthogonalMooreGrid | OrthogonalVonNeumannGrid
HexGrid = HexSingleGrid | HexMultiGrid | mesa.discrete_space.HexGrid
Network = NetworkGrid | mesa.discrete_space.Network


class SpaceRenderer:
    """Renders Mesa spaces with agents and property layers using different backends."""

    def __init__(self, model, backend: str = "matplotlib", ax: Axes | None = None):
        """Initialize the space renderer.

        Args:
            model: Mesa model containing the space to render
            backend: Rendering backend ('matplotlib' or 'altair')
            ax: Matplotlib axes (ignored for altair backend)
        """
        self.space = getattr(model, "grid", None)
        if self.space is None:
            self.space = getattr(model, "space", None)
        self.backend = backend
        self.space_drawer = self._get_space_drawer()

        # Initialize mesh storage
        self.space_mesh = None
        self.agent_mesh = None
        self.propertylayer_mesh = None

        # Handle axis management
        if self.backend == "matplotlib":
            if ax is None:
                fig, ax = plt.subplots()
                self.fig = fig
            self.ax = ax
        else:
            self.ax = None
            warnings.warn(
                "Altair backend does not support direct axis management. ",
                UserWarning,
                stacklevel=2,
            )

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

            mapped_arguments["loc"] = pos[x]

        return mapped_arguments

    # Structure drawing methods
    def draw_structure(self, ax: Axes | None = None):
        """Draw the space structure (grid lines, etc.)."""
        if self.backend == "matplotlib":
            ax = ax if ax is not None else self.ax
            self.space_mesh = self.space_drawer.draw_matplotlib(ax)
            return self.space_mesh
        else:
            self.space_mesh = self.space_drawer.draw_altair()
            return self.space_mesh

    # Agent data collection methods
    def _get_agent_pos(self, agent, space):
        """Get agent position based on space type."""
        if isinstance(space, NetworkGrid):
            return agent.pos, agent.pos
        elif isinstance(space, Network):
            return agent.cell.coordinate, agent.cell.coordinate
        else:
            x = agent.pos[0] if agent.pos is not None else agent.cell.coordinate[0]
            y = agent.pos[1] if agent.pos is not None else agent.cell.coordinate[1]
            return x, y

    def mpl_collect_agent_data(
        self,
        space: OrthogonalGrid | HexGrid | Network | ContinuousSpace | VoronoiGrid,
        agent_portrayal: Callable,
        default_size: float | None = None,
    ) -> dict:
        """Collect plotting data for all agents in the space.

        Args:
            space: The space containing the agents
            agent_portrayal: Callable that returns AgentPortrayalStyle for each agent
            default_size: Default marker size if not specified

        Returns:
            Dictionary containing agent plotting data arrays
        """
        # Initialize data collection arrays
        arguments = {
            "loc": [],
            "s": [],
            "c": [],
            "marker": [],
            "zorder": [],
            "alpha": [],
            "edgecolors": [],
            "linewidths": [],
        }

        # Import here to prevent circular imports
        from mesa.visualization.components import AgentPortrayalStyle

        # Get default values from AgentPortrayalStyle
        style_fields = {f.name: f.default for f in fields(AgentPortrayalStyle)}
        class_default_size = style_fields.get("size")

        for agent in space.agents:
            portray_input = agent_portrayal(agent)

            if isinstance(portray_input, dict):
                warnings.warn(
                    "Returning a dict from agent_portrayal is deprecated. "
                    "Please return an AgentPortrayalStyle instance instead.",
                    PendingDeprecationWarning,
                    stacklevel=2,
                )
                # Handle legacy dict input
                dict_data = portray_input.copy()
                agent_x, agent_y = self._get_agent_pos(agent, space)

                # Extract values with defaults
                aps = AgentPortrayalStyle(
                    x=agent_x,
                    y=agent_y,
                    size=dict_data.pop("size", style_fields.get("size")),
                    color=dict_data.pop("color", style_fields.get("color")),
                    marker=dict_data.pop("marker", style_fields.get("marker")),
                    zorder=dict_data.pop("zorder", style_fields.get("zorder")),
                    alpha=dict_data.pop("alpha", style_fields.get("alpha")),
                    edgecolors=dict_data.pop("edgecolors", None),
                    linewidths=dict_data.pop(
                        "linewidths", style_fields.get("linewidths")
                    ),
                )

                # Warn about unused keys
                if dict_data:
                    ignored_keys = list(dict_data.keys())
                    warnings.warn(
                        f"The following keys were ignored: {', '.join(ignored_keys)}",
                        UserWarning,
                        stacklevel=2,
                    )
            else:
                aps = portray_input
                # Set defaults if not provided
                if aps.edgecolors is None:
                    aps.edgecolors = aps.color
                if aps.x is None and aps.y is None:
                    aps.x, aps.y = self._get_agent_pos(agent, space)

            # Collect agent data
            arguments["loc"].append((aps.x, aps.y))

            # Determine final size
            size_to_collect = aps.size or default_size or class_default_size
            arguments["s"].append(size_to_collect)
            arguments["c"].append(aps.color)
            arguments["marker"].append(aps.marker)
            arguments["zorder"].append(aps.zorder)
            arguments["alpha"].append(aps.alpha)
            if aps.edgecolors is not None:
                arguments["edgecolors"].append(aps.edgecolors)
            arguments["linewidths"].append(aps.linewidths)

        # Convert to numpy arrays
        data = {
            k: (np.asarray(v, dtype=object) if k == "marker" else np.asarray(v))
            for k, v in arguments.items()
        }

        # Handle marker array specially to preserve tuples
        arr = np.empty(len(arguments["marker"]), dtype=object)
        arr[:] = arguments["marker"]
        data["marker"] = arr

        return data

    def altair_collect_agent_data(
        self,
        space: OrthogonalGrid | HexGrid | Network | ContinuousSpace | VoronoiGrid,
        agent_portrayal: Callable,
        default_size: float | None = None,
    ) -> dict:
        """Collect plotting data for all agents in the space for Altair.

        Args:
            space: The space containing the agents
            agent_portrayal: Callable that returns AgentPortrayalStyle for each agent
            default_size: Default marker size if not specified

        Returns:
            Dictionary containing agent plotting data arrays
        """
        # Initialize data collection arrays
        arguments = {
            "loc": [],
            "size": [],
            "color": [],
            "shape": [],
            "order": [],  # z-order
            "opacity": [],
            "stroke": [],  # Stroke color
            "strokeWidth": [],
            "filled": [],
        }

        from mesa.visualization.components import AgentPortrayalStyle

        style_fields = {f.name: f.default for f in fields(AgentPortrayalStyle)}
        class_default_size = style_fields.get("size")

        # Marker mapping from Matplotlib to Altair
        marker_to_shape_map = {
            "o": "circle",
            "s": "square",
            "D": "diamond",
            "^": "triangle-up",
            "v": "triangle-down",
            "<": "triangle-left",
            ">": "triangle-right",
            "+": "cross",
            "x": "cross",  # Both '+' and 'x' map to cross in Altair
            ".": "circle",  # Small point becomes circle
            "1": "triangle-down",  # tri_down
            "2": "triangle-up",  # tri_up
            "3": "triangle-left",  # tri_left
            "4": "triangle-right",  # tri_right
        }

        for agent in space.agents:
            portray_input = agent_portrayal(agent)
            aps: AgentPortrayalStyle

            if isinstance(portray_input, dict):
                warnings.warn(
                    "Returning a dict from agent_portrayal is deprecated. "
                    "Please return an AgentPortrayalStyle instance instead.",
                    PendingDeprecationWarning,
                    stacklevel=2,
                )
                dict_data = portray_input.copy()
                agent_x, agent_y = self._get_agent_pos(agent, space)

                aps = AgentPortrayalStyle(
                    x=agent_x,
                    y=agent_y,
                    size=dict_data.pop("size", style_fields.get("size")),
                    color=dict_data.pop("color", style_fields.get("color")),
                    marker=dict_data.pop("marker", style_fields.get("marker")),
                    zorder=dict_data.pop("zorder", style_fields.get("zorder")),
                    alpha=dict_data.pop("alpha", style_fields.get("alpha")),
                    edgecolors=dict_data.pop(
                        "edgecolors", style_fields.get("edgecolors")
                    ),
                    linewidths=dict_data.pop(
                        "linewidths", style_fields.get("linewidths")
                    ),
                )
                if dict_data:
                    ignored_keys = list(dict_data.keys())
                    warnings.warn(
                        f"The following keys were ignored from dict portrayal: {', '.join(ignored_keys)}",
                        UserWarning,
                        stacklevel=2,
                    )
            else:
                aps = portray_input
                if aps.x is None and aps.y is None:
                    aps.x, aps.y = self._get_agent_pos(agent, space)

            arguments["loc"].append((aps.x, aps.y))

            size_to_collect = aps.size if aps.size is not None else default_size
            if size_to_collect is None:
                size_to_collect = class_default_size
            arguments["size"].append(size_to_collect)

            arguments["color"].append(
                aps.color if aps.color is not None else style_fields.get("color")
            )

            # Map marker to Altair shape if defined, else use raw marker
            raw_marker = (
                aps.marker if aps.marker is not None else style_fields.get("marker")
            )
            shape_value = marker_to_shape_map.get(raw_marker, raw_marker)
            if shape_value is None:
                warnings.warn(
                    f"Marker '{raw_marker}' is not supported in Altair. "
                    "Using 'circle' as default.",
                    UserWarning,
                    stacklevel=2,
                )
                shape_value = "circle"
            arguments["shape"].append(shape_value)

            arguments["order"].append(
                aps.zorder if aps.zorder is not None else style_fields.get("zorder")
            )
            arguments["opacity"].append(
                aps.alpha if aps.alpha is not None else style_fields.get("alpha")
            )
            arguments["stroke"].append(aps.edgecolors)
            arguments["strokeWidth"].append(
                aps.linewidths
                if aps.linewidths is not None
                else style_fields.get("linewidths")
            )

            # FIXME: Kind of stupid logic.
            # filled: True if edgecolors are defined, False otherwise.
            filled_value = aps.edgecolors is not None
            arguments["filled"].append(filled_value)

        final_data = {}
        for k, v in arguments.items():
            if k == "shape":
                # Ensure shape is an object array
                arr = np.empty(len(v), dtype=object)
                arr[:] = v
                final_data[k] = arr
            elif k in ["x", "y", "size", "order", "opacity", "strokeWidth"]:
                final_data[k] = np.asarray(v, dtype=float)
            else:
                final_data[k] = np.asarray(v)

        return final_data

    # Agent drawing methods
    def _draw_agents_matplotlib(self, ax: Axes | None, arguments, **kwargs):
        """Draw agents using matplotlib backend."""
        loc = arguments.pop("loc")
        x, y = loc[:, 0], loc[:, 1]
        marker = arguments.pop("marker")
        zorder = arguments.pop("zorder")

        # Check for conflicting parameters
        for entry in ["edgecolors", "linewidths", "alpha"]:
            if len(arguments[entry]) == 0:
                arguments.pop(entry)
            elif entry in kwargs:
                raise ValueError(
                    f"{entry} specified in both agent portrayal and kwargs"
                )

        # Draw agents grouped by marker and z-order for efficiency
        for mark in set(marker):
            mark_mask = np.array([m == mark for m in marker])
            for z_order in np.unique(zorder):
                zorder_mask = zorder == z_order
                logical = mark_mask & zorder_mask

                if not np.any(logical):
                    continue

                ax.scatter(
                    x[logical],
                    y[logical],
                    marker=mark,
                    zorder=z_order,
                    **{k: v[logical] for k, v in arguments.items()},
                    **kwargs,
                )
        return ax

    def _draw_agents_altair(
        self, arguments, chart_width=450, chart_height=350, **kwargs
    ):
        """Draw agents using altair backend."""
        # Convert arguments to a DataFrame
        df_data = {
            "x": arguments["loc"][:, 0],
            "y": arguments["loc"][:, 1],
            "size": arguments["size"],
            "shape": arguments["shape"],
            "opacity": arguments["opacity"],
            "strokeWidth": arguments["strokeWidth"],
            "original_color": arguments["color"],
            "is_filled": arguments["filled"],
            "original_stroke": arguments["stroke"],
        }
        df = pd.DataFrame(df_data)

        # To ensure altair doesn't pickup random shapes
        unique_shape_names_in_data = df["shape"].unique().tolist()

        fill_colors = []
        stroke_colors = []

        for i in range(len(df)):
            filled = df["is_filled"][i]
            main_color = df["original_color"][i]
            # Ensure 'original_stroke' is None if it's np.nan or other non-string None types
            stroke_spec = (
                df["original_stroke"][i]
                if isinstance(df["original_stroke"][i], str)
                else None
            )

            if filled:
                fill_colors.append(main_color)
                stroke_colors.append(stroke_spec)
            else:
                fill_colors.append(None)
                stroke_colors.append(main_color)

        df["viz_fill_color"] = fill_colors
        df["viz_stroke_color"] = stroke_colors

        # Tooltip list for interactivity
        # FIXME: Add more fields to tooltip (preferably from agent_portrayal)
        tooltip_list = ["x", "y"]

        chart = (
            alt.Chart(df)
            .mark_point()
            .encode(
                x=alt.X(
                    "x:Q",
                    title="X",
                    scale=alt.Scale(
                        type="linear", domain=[-0.5, self.space.width - 0.5]
                    ),
                ),
                y=alt.Y(
                    "y:Q",
                    title="Y",
                    scale=alt.Scale(
                        type="linear", domain=[-0.5, self.space.height - 0.5]
                    ),
                ),
                size=alt.Size("size:Q", legend=None),
                shape=alt.Shape(
                    "shape:N",
                    scale=alt.Scale(
                        domain=unique_shape_names_in_data,
                        range=unique_shape_names_in_data,
                    ),
                    title="Shape",
                ),
                opacity=alt.Opacity(
                    "opacity:Q",
                    title="Opacity",
                    scale=alt.Scale(domain=[0, 1], range=[0, 1]),
                ),
                fill=alt.Fill("viz_fill_color:N", scale=None, title="Fill Color"),
                stroke=alt.Stroke(
                    "viz_stroke_color:N", scale=None, title="Stroke Color"
                ),
                strokeWidth=alt.StrokeWidth("strokeWidth:Q", title="Stroke Width"),
                tooltip=tooltip_list,
            )
            .properties(
                title="Agent Plot (Altair)", width=chart_width, height=chart_height
            )
        )

        return chart

    def draw_agents(self, agent_portrayal, ax: Axes | None = None, **kwargs):
        """Draw agents on the space."""
        self.agent_portrayal = agent_portrayal

        if self.backend == "matplotlib":
            ax = ax if ax is not None else self.ax

            arguments = self.mpl_collect_agent_data(
                self.space, agent_portrayal, default_size=self.space_drawer.s_default
            )
            arguments = self._map_coordinates(arguments)
            self.agent_mesh = self._draw_agents_matplotlib(ax, arguments, **kwargs)

            return self.agent_mesh

        else:
            arguments = self.altair_collect_agent_data(
                self.space, agent_portrayal, default_size=self.space_drawer.s_default
            )
            arguments = self._map_coordinates(arguments)
            self.agent_mesh = self._draw_agents_altair(arguments, **kwargs)
            return self.agent_mesh

    # Property layer drawing methods
    def _draw_propertylayer_matplotlib(self, space, propertylayer_portrayal, ax):
        """Draw property layers using matplotlib backend."""
        # Import here to avoid circular imports
        from mesa.visualization.components import PropertyLayerStyle

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
            property_layers = space.properties
        except AttributeError:
            # new style spaces
            property_layers = space._mesa_property_layers

        # Convert portrayal to callable if needed
        if isinstance(propertylayer_portrayal, dict):
            callable_portrayal = _dict_to_callable(propertylayer_portrayal)
        else:
            callable_portrayal = propertylayer_portrayal

        # Draw each layer
        for layer_name in property_layers:
            if layer_name == "empty":
                continue

            layer = property_layers.get(layer_name)
            portrayal = callable_portrayal(layer)

            if portrayal is None:
                continue

            data = layer.data.astype(float) if layer.data.dtype == bool else layer.data

            # Check dimensions
            if (space.width, space.height) != data.shape:
                warnings.warn(
                    f"Layer {layer_name} dimensions ({data.shape}) "
                    f"don't match space dimensions ({space.width}, {space.height})",
                    UserWarning,
                    stacklevel=2,
                )

            # Get portrayal parameters
            color = portrayal.color
            colormap = portrayal.colormap
            alpha = portrayal.alpha
            vmin = portrayal.vmin if portrayal.vmin is not None else np.min(data)
            vmax = portrayal.vmax if portrayal.vmax is not None else np.max(data)

            # Set up colormap
            if color:
                rgba_color = to_rgba(color)
                cmap = LinearSegmentedColormap.from_list(
                    layer_name, [(0, 0, 0, 0), (*rgba_color[:3], alpha)]
                )
            elif colormap:
                cmap = colormap
                if isinstance(cmap, list):
                    cmap = LinearSegmentedColormap.from_list(layer_name, cmap)
                elif isinstance(cmap, str):
                    cmap = plt.get_cmap(cmap)
            else:
                raise ValueError(
                    f"PropertyLayer {layer_name} must include 'color' or 'colormap'"
                )

            # Draw based on space type
            if isinstance(space, OrthogonalGrid):
                if color:
                    data = data.T
                    normalized_data = (data - vmin) / (vmax - vmin)
                    rgba_data = np.full((*data.shape, 4), rgba_color)
                    rgba_data[..., 3] *= normalized_data * alpha
                    rgba_data = np.clip(rgba_data, 0, 1)
                    ax.imshow(rgba_data, origin="lower")
                else:
                    ax.imshow(
                        data.T,
                        cmap=cmap,
                        alpha=alpha,
                        vmin=vmin,
                        vmax=vmax,
                        origin="lower",
                    )
            elif isinstance(space, HexGrid):
                hexagons = self.space_drawer.hexagons
                norm = Normalize(vmin=vmin, vmax=vmax)
                colors = data.ravel()

                if color:
                    normalized_colors = np.clip(norm(colors), 0, 1)
                    rgba_colors = np.full((len(colors), 4), rgba_color)
                    rgba_colors[:, 3] = normalized_colors * alpha
                else:
                    rgba_colors = cmap(norm(colors))
                    rgba_colors[..., 3] *= alpha

                collection = PolyCollection(hexagons, facecolors=rgba_colors, zorder=-1)
                ax.add_collection(collection)
            else:
                raise NotImplementedError(
                    f"PropertyLayer visualization not implemented for {type(space)}"
                )

            # Add colorbar if requested
            if portrayal.colorbar:
                norm = Normalize(vmin=vmin, vmax=vmax)
                sm = ScalarMappable(norm=norm, cmap=cmap)
                sm.set_array([])
                plt.colorbar(sm, ax=ax, label=layer_name)

        return ax

    def _draw_propertylayer_altair(
        self, space, propertylayer_portrayal, chart_width=450, chart_height=350
    ):
        """Draw property layers using altair backend."""
        # Import here to avoid circular imports
        from mesa.visualization.components import PropertyLayerStyle

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
            property_layers = space.properties
        except AttributeError:
            # new style spaces
            property_layers = space._mesa_property_layers

        base = None
        bar_chart_viz = None

        # Convert portrayal to callable if needed
        if isinstance(propertylayer_portrayal, dict):
            callable_portrayal = _dict_to_callable(propertylayer_portrayal)
        else:
            callable_portrayal = propertylayer_portrayal

        for layer_name in property_layers:
            if layer_name == "empty":
                continue

            layer = property_layers.get(layer_name)
            portrayal = callable_portrayal(layer)

            if portrayal is None:
                continue

            data = layer.data.astype(float) if layer.data.dtype == bool else layer.data

            # Check dimensions
            if (space.width, space.height) != data.shape:
                warnings.warn(
                    f"Layer {layer_name} dimensions ({data.shape}) do not match space dimensions ({space.width}, {space.height}).",
                    UserWarning,
                    stacklevel=2,
                )
                continue

            # Get portrayal parameters
            color = portrayal.color
            colormap = portrayal.colormap
            alpha = portrayal.alpha
            vmin = portrayal.vmin if portrayal.vmin is not None else np.min(data)
            vmax = portrayal.vmax if portrayal.vmax is not None else np.max(data)

            # Prepare data for Altair (convert 2D array to a long-form DataFrame)
            df = pd.DataFrame(
                {
                    "x": np.repeat(np.arange(data.shape[0]), data.shape[1]),
                    "y": np.tile(np.arange(data.shape[1]), data.shape[0]),
                    "value": data.flatten(),
                }
            )

            current_chart = None
            if color:
                # Create a function to map values to RGBA colors with proper opacity scaling
                def apply_rgba(
                    val, v_min=vmin, v_max=vmax, a=alpha, p_color=portrayal.color
                ):
                    # Normalize value to range [0,1] and clamp
                    normalized = max(
                        0,
                        min(
                            ((val - v_min) / (v_max - v_min))
                            if (v_max - v_min) != 0
                            else 0.5,
                            1,
                        ),
                    )

                    # Scale opacity by alpha parameter
                    opacity = normalized * a

                    # Convert color to RGB components
                    rgb_color_val = to_rgb(p_color)
                    r = int(rgb_color_val[0] * 255)
                    g = int(rgb_color_val[1] * 255)
                    b = int(rgb_color_val[2] * 255)
                    return f"rgba({r}, {g}, {b}, {opacity:.2f})"

                # Apply color mapping to each value in the dataset
                df["color_str"] = df["value"].apply(apply_rgba)

                # Create chart for the property layer
                current_chart = (
                    alt.Chart(df)
                    .mark_rect()
                    .encode(
                        x=alt.X("x:O", axis=None),
                        y=alt.Y("y:O", axis=None),
                        fill=alt.Fill("color_str:N", scale=None),
                    )
                    .properties(
                        width=chart_width, height=chart_height, title=layer_name
                    )
                )
                base = (
                    alt.layer(current_chart, base)
                    if base is not None
                    else current_chart
                )

                # Add colorbar if specified in portrayal
                if portrayal.colorbar:
                    # Extract RGB components from base color
                    rgb_color_val = to_rgb(portrayal.color)
                    r_int = int(rgb_color_val[0] * 255)
                    g_int = int(rgb_color_val[1] * 255)
                    b_int = int(rgb_color_val[2] * 255)

                    # Define gradient endpoints
                    min_color_str = f"rgba({r_int},{g_int},{b_int},0)"
                    max_color_str = f"rgba({r_int},{g_int},{b_int},{alpha:.2f})"

                    # Define colorbar dimensions
                    colorbar_height = 20
                    colorbar_width = chart_width

                    # Create dataframe for gradient visualization
                    df_gradient = pd.DataFrame({"x_grad": [0, 1], "y_grad": [0, 1]})

                    # Create evenly distributed tick values
                    axis_values = np.linspace(vmin, vmax, 11)
                    tick_positions = np.linspace(0, colorbar_width, 11)

                    # Prepare data for axis and labels
                    axis_data = pd.DataFrame(
                        {"value_axis": axis_values, "x_axis": tick_positions}
                    )

                    # Create colorbar with linear gradient
                    colorbar_chart_obj = (
                        alt.Chart(df_gradient)
                        .mark_rect(
                            x=0,
                            y=0,
                            width=colorbar_width,
                            height=colorbar_height,
                            color=alt.Gradient(
                                gradient="linear",
                                stops=[
                                    alt.GradientStop(color=min_color_str, offset=0),
                                    alt.GradientStop(color=max_color_str, offset=1),
                                ],
                                x1=0,
                                x2=1,  # Horizontal gradient
                                y1=0,
                                y2=0,  # Keep y constant
                            ),
                        )
                        .encode(
                            x=alt.value(chart_width / 2), y=alt.value(0)
                        )  # Center colorbar
                        .properties(width=colorbar_width, height=colorbar_height)
                    )
                    # Add tick marks to colorbar
                    axis_chart = (
                        alt.Chart(axis_data)
                        .mark_tick(thickness=2, size=8)
                        .encode(
                            x=alt.X("x_axis:Q", axis=None),
                            y=alt.value(colorbar_height - 2),
                        )
                    )
                    # Add value labels below tick marks
                    text_labels = (
                        alt.Chart(axis_data)
                        .mark_text(baseline="top", fontSize=10, dy=0)
                        .encode(
                            x=alt.X("x_axis:Q"),
                            text=alt.Text("value_axis:Q", format=".1f"),
                            y=alt.value(colorbar_height + 10),
                        )
                    )
                    # Add title to colorbar
                    title_chart = (
                        alt.Chart(pd.DataFrame([{"text_title": layer_name}]))
                        .mark_text(
                            fontSize=12,
                            fontWeight="bold",
                            baseline="bottom",
                            align="center",
                        )
                        .encode(
                            text="text_title:N",
                            x=alt.value(colorbar_width / 2),
                            y=alt.value(colorbar_height + 40),
                        )
                    )
                    # Combine all colorbar components
                    combined_colorbar = alt.layer(
                        colorbar_chart_obj, axis_chart, text_labels, title_chart
                    ).properties(width=colorbar_width, height=colorbar_height + 50)

                    bar_chart_viz = (
                        alt.vconcat(bar_chart_viz, combined_colorbar)
                        .resolve_scale(color="independent")
                        .configure_view(stroke=None)
                        if bar_chart_viz is not None
                        else combined_colorbar
                    )

            elif colormap:
                cmap = colormap
                cmap_scale = alt.Scale(scheme=cmap, domain=[vmin, vmax])

                current_chart = (
                    alt.Chart(df)
                    .mark_rect(opacity=alpha)
                    .encode(
                        x=alt.X("x:O", axis=None),
                        y=alt.Y("y:O", axis=None),
                        color=alt.Color(
                            "value:Q",
                            scale=cmap_scale,
                            title=layer_name,
                            legend=alt.Legend(title=layer_name)
                            if portrayal.colorbar
                            else None,
                        ),
                    )
                    .properties(width=chart_width, height=chart_height)
                )
                base = (
                    alt.layer(current_chart, base)
                    if base is not None
                    else current_chart
                )
            else:
                raise ValueError(
                    f"PropertyLayer {layer_name} portrayal must include 'color' or 'colormap'."
                )
        return base, bar_chart_viz

    def draw_propertylayer(self, propertylayer_portrayal, ax: Axes | None = None):
        """Draw property layers on the space."""
        self.propertylayer_portrayal = propertylayer_portrayal

        if self.backend == "matplotlib":
            ax = ax if ax is not None else self.ax
            self.propertylayer_mesh = self._draw_propertylayer_matplotlib(
                self.space, propertylayer_portrayal, ax
            )
            return self.propertylayer_mesh
        else:
            self.propertylayer_mesh = self._draw_propertylayer_altair(
                self.space, propertylayer_portrayal
            )
            return self.propertylayer_mesh

    # Main rendering method
    def render(
        self,
        agent_portrayal,
        propertylayer_portrayal=None,
        ax: Axes | None = None,
        **kwargs,
    ):
        """Render the complete space with structure, agents, and property layers."""
        if self.backend == "matplotlib":
            ax = ax if ax is not None else self.ax

            self.draw_structure(ax)
            self.draw_agents(agent_portrayal, ax, **kwargs)
            if propertylayer_portrayal is not None:
                self.draw_propertylayer(propertylayer_portrayal, ax)

            return ax
        else:
            # TODO: Implement Altair rendering pipeline
            raise NotImplementedError(
                "Altair rendering is not yet implemented. "
                "Please use the matplotlib backend for now."
            )

    @property
    def canvas(self):
        """Get the matplotlib axis used for rendering."""
        if self.backend == "matplotlib":
            return self.ax
        else:
            # TODO: Implement Altair chart retrieval
            return None

    def clear_meshes(self):
        """Clear all stored mesh objects."""
        self.space_mesh = None
        self.agent_mesh = None
        self.propertylayer_mesh = None
