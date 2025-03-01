"""Altair based solara components for visualization mesa spaces."""

import contextlib
import math
import itertools
import warnings
from collections.abc import Callable
from functools import lru_cache

import solara

import mesa
import mesa.experimental
from mesa.experimental.cell_space import HexGrid

with contextlib.suppress(ImportError):
    import altair as alt

from mesa.experimental.cell_space import Grid
from mesa.space import ContinuousSpace, NetworkGrid, _Grid
from mesa.visualization.utils import update_counter
import numpy as np

def make_space_altair(*args, **kwargs):
    """Create an Altair chart component for visualizing model space (deprecated).

    This function is deprecated. Use make_altair_space_component instead.
    """
    warnings.warn(
        "make_space_altair has been renamed to make_altair_space_component",
        DeprecationWarning,
        stacklevel=2,
    )
    return make_altair_space_component(*args, **kwargs)


def make_altair_space_component(*args, **kwargs):
    """Create an Altair-based space visualization component.

    Args:
        *args: Positional arguments passed to make_altair_space
        **kwargs: Keyword arguments passed to make_altair_space

    Returns:
        function: A function that creates an Altair space visualization component

    See Also:
        make_altair_space: The underlying implementation
    """
    return make_altair_space(*args, **kwargs)


def make_altair_space(
    agent_portrayal, propertylayer_portrayal, post_process, **space_drawing_kwargs
):
    """Create an Altair-based space visualization component.

    Args:
        agent_portrayal: Function to portray agents.
        propertylayer_portrayal: not yet implemented
        post_process :A user specified callable that will be called with the Chart instance from Altair. Allows for fine tuning plots (e.g., control ticks)
        space_drawing_kwargs : not yet implemented

    ``agent_portrayal`` is called with an agent and should return a dict. Valid fields in this dict are "color",
    "size", "marker", and "zorder". Other field are ignored and will result in a user warning.

    Returns:
        function: A function that creates a SpaceAltair component
    """
    if agent_portrayal is None:
        def agent_portrayal(a):
            return {"id": a.unique_id}

    def MakeSpaceAltair(model):
        return SpaceAltair(model, agent_portrayal, post_process=post_process)

    return MakeSpaceAltair


def make_altair_plot_component(
    measure: str | dict[str, str] | list[str] | tuple[str],
    post_process: Callable | None = None,
    width: int = 500,
    height: int = 300,
):
    """Create an Altair plotting component for specified measures.

    Args:
        measure: Measure(s) to plot. Can be:
            - str: Single measure name
            - dict: Mapping of measure names to colors
            - list/tuple: Multiple measure names
        post_process: Optional callable for chart post-processing
        width: Chart width in pixels
        height: Chart height in pixels

    Returns:
        function: A function that creates a PlotAltair component
    """

    def MakePlotAltair(model):
        return PlotAltair(
            model, measure, post_process=post_process, width=width, height=height
        )

    return MakePlotAltair


@solara.component
def PlotAltair(
    model,
    measure: str | dict[str, str] | list[str] | tuple[str],
    post_process: Callable[[alt.Chart], alt.Chart] | None = None,
    width: int = 500,
    height: int = 300,
) -> solara.FigureAltair:
    """Create an Altair plot for model data.

    Args:
        model: The mesa.Model instance.
        measure (str | dict[str, str] | list[str] | tuple[str]): Measure(s) to plot.
        post_process: An optional callable that takes an Altair Chart object as
                      input and returns a modified Chart object. This allows
                      for customization of the plot (e.g., adding annotations,
                      changing axis labels).
        width: The width of the chart in pixels.
        height: The height of the chart in pixels.

    Returns:
        A solara.FigureAltair component displaying the generated Altair chart.
    """
    update_counter.get()
    df = model.datacollector.get_model_vars_dataframe().reset_index()

    if isinstance(measure, str):
        # Single measure - no transformation needed
        chart = (
            alt.Chart(df)
            .encode(
                x="Step:Q",
                y=alt.Y(f"{measure}:Q", title=measure),
                tooltip=[alt.Tooltip("Step:Q"), alt.Tooltip(f"{measure}:Q")],
            )
            .mark_line()
        )

    elif isinstance(measure, list | tuple):
        # Multiple measures - melt dataframe
        value_vars = list(measure)
        melted_df = df.melt(
            "Step", value_vars=value_vars, var_name="Measure", value_name="Value"
        )

        chart = (
            alt.Chart(melted_df)
            .encode(
                x="Step:Q",
                y=alt.Y("Value:Q"),
                color="Measure:N",
                tooltip=["Step:Q", "Value:Q", "Measure:N"],
            )
            .mark_line()
        )

    elif isinstance(measure, dict):
        # Dictionary with colors - melt dataframe
        value_vars = list(measure.keys())
        melted_df = df.melt(
            "Step", value_vars=value_vars, var_name="Measure", value_name="Value"
        )

        # Create color scale from measure dict
        domain = list(measure.keys())
        range_ = list(measure.values())

        chart = (
            alt.Chart(melted_df)
            .encode(
                x="Step:Q",
                y=alt.Y("Value:Q"),
                color=alt.Color(
                    "Measure:N", scale=alt.Scale(domain=domain, range=range_)
                ),
                tooltip=["Step:Q", "Value:Q", "Measure:N"],
            )
            .mark_line()
        )

    else:
        raise ValueError("Unsupported measure type")

    # Configure chart properties
    chart = chart.properties(width=width, height=height).configure_axis(grid=True)

    if post_process is not None:
        chart = post_process(chart)

    return solara.FigureAltair(chart)


@solara.component
def SpaceAltair(
    model, agent_portrayal, dependencies: list[any] | None = None, post_process=None
):
    """Create an Altair-based space visualization component.

    Args:
        model: The mesa.Model instance containing the space to visualize.
               The model must have a `grid` or `space` attribute that
               represents the space (e.g., Grid, ContinuousSpace, NetworkGrid).
        agent_portrayal: A callable that takes an agent as input and returns
                         a dictionary specifying how the agent should be
                         visualized.  The dictionary can contain the following keys:
                           - "color":  A string representing the agent's color (e.g., "red", "#FF0000").
                           - "size":   A number representing the agent's size.
                           - "tooltip": A string to display as a tooltip when hovering over the agent.
                           - Any other Vega-Lite mark properties that are supported by Altair.
        dependencies: A list of dependencies that trigger a re-render of the
                      component when they change.  This can be used to update
                      the visualization when the model state changes.
        post_process: An optional callable that takes an Altair Chart object
                      as input and returns a modified Chart object. This allows
                      for customization of the plot (e.g., adding annotations,
                      changing axis labels).

    Returns:
        A solara.FigureAltair instance, which is a Solara component that
        renders the Altair chart.

    """
    # Force update on dependencies change
    update_counter.get()
    space = getattr(model, "grid", None)
    if space is None:
        space = model.space

    chart = _draw_grid(space, agent_portrayal)
    if post_process is not None:
        chart = post_process(chart)

    # Return the rendered chart
    return solara.FigureAltair(chart)


def axial_to_pixel(q, r, size=1):
    """Convert axial coordinates (q, r) to pixel coordinates for hexagonal grid."""
    x = size * math.sqrt(3) * (q + r / 2)
    y = size * 1.5 * r
    return x, y


def _draw_grid(space, agent_portrayal):
    """Create Altair visualization for any supported space type.

    This function acts as a dispatcher, calling the appropriate
    `_draw_*_grid` function based on the type of space provided.

    Args:
        space: The mesa.space object to visualize (e.g., Grid, ContinuousSpace,
               NetworkGrid).
        agent_portrayal: A callable that takes an agent as input and returns
                         a dictionary specifying how the agent should be
                         visualized.

    Returns:
        An Altair Chart object representing the visualization of the space
        and its agents.  Returns a text chart "No agents" if there are no agents.

    """
    # Handle empty state first
    if not space.agents:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)

    match space:
        case HexGrid():
            return _draw_hex_grid(space, agent_portrayal)
        case Grid():
            return _draw_discrete_grid(space, agent_portrayal)
        case _Grid():
            return _draw_legacy_grid(space, agent_portrayal)
        case NetworkGrid():
            return _draw_network_grid(space, agent_portrayal)
        case ContinuousSpace() | mesa.experimental.continuous_space.ContinuousSpace():
            return _draw_continuous_space(space, agent_portrayal)
        case _:
            raise NotImplementedError(f"Unsupported space type: {type(space)}")


def _draw_discrete_grid(space, agent_portrayal):
    """Create Altair visualization for Discrete Grid."""
    all_agent_data = []
    
    # Collect agent data
    for cell in space.all_cells:
        for agent in cell.agents:
            data = agent_portrayal(agent)
            data.update({
                "x": float(cell.coordinate[0]), 
                "y": float(cell.coordinate[1])
            })
            all_agent_data.append(data)

    if not all_agent_data:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)

    # Create base chart
    base = alt.Chart(alt.Data(values=all_agent_data)).properties(
        width=280, height=280
    )

    # Configure encodings
    encodings = {
        "x": alt.X(
            "x:Q",
            scale=alt.Scale(domain=[0, space.width-1]),
            axis=alt.Axis(grid=True)  # Enable grid
        ),
        "y": alt.Y(
            "y:Q", 
            scale=alt.Scale(domain=[0, space.height-1]),
            axis=alt.Axis(grid=True)  # Enable grid
        ),
    }

    # Add color encoding if present
    if "color" in all_agent_data[0]:
        encodings["color"] = alt.Color("color:N")

    # Add size encoding if present 
    if "size" in all_agent_data:
        encodings["size"] = alt.Size("size:Q")
    else:
        # Default size based on grid dimensions
        point_size = 30000 / min(space.width, space.height)**2
        base = base.mark_point(size=point_size, filled=True)

    # Create final chart with encodings
    chart = base.encode(**encodings)

    return chart


def _draw_legacy_grid(space, agent_portrayal):
    """Create Altair visualization for Legacy Grid."""
    all_agent_data = []
    for content, (x, y) in space.coord_iter():
        if not content:
            continue
        agents = [content] if not hasattr(content, "__iter__") else content
        for agent in agents:
            data = agent_portrayal(agent)
            data.update({"x": x, "y": y})
            all_agent_data.append(data)

    if not all_agent_data:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)

    invalid_tooltips = ["color", "size", "x", "y"]
    x_y_type = "ordinal"

    encoding_dict = {
        "x": alt.X("x", axis=alt.Axis(grid=True), type=x_y_type),  # Enable grid
        "y": alt.Y("y", axis=alt.Axis(grid=True), type=x_y_type),  # Enable grid
        "tooltip": [
            alt.Tooltip(key, type=alt.utils.infer_vegalite_type_for_pandas([value]))
            for key, value in all_agent_data[0].items()
            if key not in invalid_tooltips
        ],
    }

    has_color = "color" in all_agent_data[0]
    if has_color:
        encoding_dict["color"] = alt.Color("color", type="nominal")
    has_size = "size" in all_agent_data
    if has_size:
        encoding_dict["size"] = alt.Size("size", type="quantitative")

    chart = (
        alt.Chart(
            alt.Data(values=all_agent_data), encoding=alt.Encoding(**encoding_dict)
        )
        .mark_point(filled=True)
        .properties(width=280, height=280)
    )

    if not has_size:
        length = min(space.width, space.height)
        chart = chart.mark_point(size=30000 / length**2, filled=True)

    chart = chart.encode(
        x=alt.X(
            "x", axis=alt.Axis(grid=True), type=x_y_type, scale=alt.Scale(domain=(0, space.width - 1))
        ),
        y=alt.Y(
            "y", axis=alt.Axis(grid=True), type=x_y_type, scale=alt.Scale(domain=(0, space.height - 1))
        ),
    )

    return chart


@lru_cache(maxsize=1024, typed=True)
def _get_hexmesh(
    width: int, height: int, size: float = 1.0
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


def _draw_hex_grid(space, agent_portrayal):
    """Create Altair visualization for Hex Grid."""
    size = 1.0
    x_spacing = math.sqrt(3) * size
    y_spacing = 1.5 * size

    # Get cached hex mesh
    hexagons = _get_hexmesh(space.width, space.height, size)

    # Calculate bounds
    x_max = space.width * x_spacing + (space.height % 2) * (x_spacing / 2)
    y_max = space.height * y_spacing
    x_padding = size * math.sqrt(3) / 2
    y_padding = size

    # Prepare data for grid lines
    hex_lines = []
    hex_centers = []
    
    for idx, hexagon in enumerate(hexagons):
        # Calculate center of this hexagon
        x_center = sum(p[0] for p in hexagon) / 6
        y_center = sum(p[1] for p in hexagon) / 6
        
        # Calculate row and column from index
        row = idx // space.width
        col = idx % space.width
        
        # Store center
        hex_centers.append((col, row, x_center, y_center))
        
        # Create line segments
        for i in range(6):
            x1, y1 = hexagon[i]
            x2, y2 = hexagon[(i + 1) % 6]
            hex_lines.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2})

    # Create grid lines layer
    grid_lines = alt.Chart(alt.Data(values=hex_lines)).mark_rule(
        color='gray',
        strokeWidth=1,
        opacity=0.5
    ).encode(
        x='x1:Q',
        y='y1:Q',
        x2='x2:Q',
        y2='y2:Q'
    ).properties(
        width=280,
        height=280
    )

    # Create mapping from coordinate to center position
    center_map = {(col, row): (x, y) for col, row, x, y in hex_centers}

    # Create agents layer
    all_agent_data = []
    
    for cell in space.all_cells:
        for agent in cell.agents:
            data = agent_portrayal(agent)
            # Get hex center for this cell's coordinate
            coord = cell.coordinate
            if coord in center_map:
                x, y = center_map[coord]
                data.update({"x": x, "y": y})
                all_agent_data.append(data)

    if not all_agent_data:
        return grid_lines

    # Create agent points layer
    agent_layer = alt.Chart(
        alt.Data(values=all_agent_data)
    ).mark_circle(
        filled=True,
        size=150  
    ).encode(
        x=alt.X('x:Q', scale=alt.Scale(domain=[-2 * x_padding, x_max + x_padding])),
        y=alt.Y('y:Q', scale=alt.Scale(domain=[-2 * y_padding, y_max + y_padding])),
    ).properties(
        width=280,
        height=280
    )

    # Add color encoding if present
    if all_agent_data and "color" in all_agent_data[0]:
        agent_layer = agent_layer.encode(color=alt.Color("color:N"))

    if all_agent_data and "size" in all_agent_data[0]:
        agent_layer = agent_layer.encode(size=alt.Size("size:Q"))

    chart = (grid_lines + agent_layer).resolve_scale(
        x='shared',
        y='shared'
    )
    
    return chart


def _draw_network_grid(space, agent_portrayal):
    """Create Altair visualization for Network Grid."""
    all_agent_data = []
    for node in space.G.nodes():
        agents = space.G.nodes[node].get("agent", [])
        if not isinstance(agents, list):
            agents = [agents] if agents else []

        for agent in agents:
            if agent:
                data = agent_portrayal(agent)
                pos = space.G.nodes[node].get("pos", (0, 0))
                data.update({"x": pos[0], "y": pos[1]})
                all_agent_data.append(data)

    if not all_agent_data:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)

    invalid_tooltips = ["color", "size", "x", "y", "node"]
    x_y_type = "quantitative"

    # Get x, y coordinates and determine bounds
    positions = [space.G.nodes[node].get("pos", (0, 0)) for node in space.G.nodes()]
    x_values = [p[0] for p in positions]
    y_values = [p[1] for p in positions]

    # Add padding to the bounds
    padding = 0.1  # 10% padding
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values) 
    x_range = x_max - x_min
    y_range = y_max - y_min

    x_scale = alt.Scale(domain=(x_min - padding * x_range, x_max + padding * x_range))
    y_scale = alt.Scale(domain=(y_min - padding * y_range, y_max + padding * y_range))

    encoding_dict = {
        "x": alt.X("x", axis=alt.Axis(grid=True), type=x_y_type, scale=x_scale),
        "y": alt.Y("y", axis=alt.Axis(grid=True), type=x_y_type, scale=y_scale),
        "tooltip": [
            alt.Tooltip(key, type=alt.utils.infer_vegalite_type_for_pandas([value]))
            for key, value in all_agent_data[0].items()
            if key not in invalid_tooltips
        ],
    }

    has_color = "color" in all_agent_data[0]
    if has_color:
        encoding_dict["color"] = alt.Color("color", type="nominal")
    has_size = "size" in all_agent_data[0] 
    if has_size:
        encoding_dict["size"] = alt.Size("size", type="quantitative")

    chart = (
        alt.Chart(
            alt.Data(values=all_agent_data), encoding=alt.Encoding(**encoding_dict)
        )
        .mark_point(filled=True)
        .properties(width=280, height=280)
    )

    return chart


def _draw_continuous_space(space, agent_portrayal):
    """Create Altair visualization for Continuous Space."""
    all_agent_data = []
    
    for agent in space.agents:
        data = agent_portrayal(agent)
        data.update({
            "x": float(agent.pos[0]),
            "y": float(agent.pos[1])
        })
        all_agent_data.append(data)

    if not all_agent_data:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)

    base = alt.Chart(alt.Data(values=all_agent_data)).properties(
        width=280, height=280
    )

    encodings = {
        "x": alt.X(
            "x:Q",
            scale=alt.Scale(domain=[0, space.width]),
            axis=alt.Axis(grid=True)  # Enable grid
        ),
        "y": alt.Y(
            "y:Q",
            scale=alt.Scale(domain=[0, space.height]), 
            axis=alt.Axis(grid=True)  # Enable grid
        )
    }

    if "color" in all_agent_data[0]:
        encodings["color"] = alt.Color("color:N")
        
    if "size" in all_agent_data:
        encodings["size"] = alt.Size("size:Q")
    else:
        base = base.mark_point(size=100, filled=True)

    chart = base.encode(**encodings)
    
    return chart
