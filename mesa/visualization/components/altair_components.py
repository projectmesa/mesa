"""Altair based solara components for visualization mesa spaces."""

import contextlib
import itertools
import math
import warnings
from collections.abc import Callable
from functools import lru_cache

import mesa.discrete_space.network
import mesa.visualization
from mesa.visualization.mpl_space_drawing import collect_agent_data,_get_hexmesh
import solara

import mesa
import mesa.experimental
from mesa.space import HexSingleGrid,HexMultiGrid

with contextlib.suppress(ImportError):
    import altair as alt

import numpy as np

from mesa.experimental.cell_space import Grid
from mesa.space import ContinuousSpace, NetworkGrid, _Grid
from mesa.visualization.utils import update_counter
import networkx as nx

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
    # Sometimes the space is defined as model.space instead of model.grid
        space = model.space

    chart = _draw_grid(space, agent_portrayal)
    #Apply post_processing if provided
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
        case HexSingleGrid() | HexMultiGrid():
            return _draw_hex_grid(space, agent_portrayal)
        case Grid():
            return _draw_discrete_grid(space, agent_portrayal)
        case _Grid():
            return _draw_legacy_grid(space, agent_portrayal)
        case NetworkGrid()| mesa.discrete_space.network.Network():
            return _draw_network_grid(space, agent_portrayal)
        case ContinuousSpace() | mesa.experimental.continuous_space.ContinuousSpace():
            return _draw_continuous_space(space, agent_portrayal)
        case _:
            raise NotImplementedError(f"Unsupported space type: {type(space)}")



def _draw_discrete_grid(space, agent_portrayal):
    """Create Altair visualization for Discrete Grid."""
    
    # Get agent data using the collect_agent_data helper function
    raw_data = collect_agent_data(space, agent_portrayal)
    
    # Early exit if no agents
    if len(raw_data["loc"]) == 0:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)
    
    # Convert raw_data (dict of arrays) to Altair format (list of dicts)
    all_agent_data = []
    for i in range(len(raw_data["loc"])):
        agent_dict = {
            "x": float(raw_data["loc"][i][0]),
            "y": float(raw_data["loc"][i][1]),
            "color": raw_data["c"][i],
            "size": raw_data["s"][i]
        }
        # Add other properties if they exist
        if len(raw_data["alpha"]) > i:
            agent_dict["alpha"] = raw_data["alpha"][i]
        if len(raw_data["edgecolors"]) > i:
            agent_dict["edgecolor"] = raw_data["edgecolors"][i]
        if len(raw_data["linewidths"]) > i:
            agent_dict["linewidth"] = raw_data["linewidths"][i]
            
        all_agent_data.append(agent_dict)

    # Create base chart
    base = alt.Chart(alt.Data(values=all_agent_data)).properties(width=280, height=280)

    # Configure encodings
    encodings = {
        "x": alt.X(
            "x:Q",
            scale=alt.Scale(domain=[0, space.width - 1]),
            axis=alt.Axis(grid=True),  # Enable grid
        ),
        "y": alt.Y(
            "y:Q",
            scale=alt.Scale(domain=[0, space.height - 1]),
            axis=alt.Axis(grid=True),  # Enable grid
        ),
    }

    # Add color encoding if present
    if "color" in all_agent_data[0]:
        encodings["color"] = alt.Color("color:N")

    # Add size encoding if present 
    if "size" in all_agent_data[0]:
        encodings["size"] = alt.Size("size:Q")
        chart = base.mark_point(filled=True).encode(**encodings)
    else:
        # Default size based on grid dimensions
        point_size = 30000 / min(space.width, space.height)**2
        chart = base.mark_point(size=point_size, filled=True).encode(**encodings)

    return chart


def _draw_legacy_grid(space, agent_portrayal):
    """Create Altair visualization for Legacy Grid."""
    all_agent_data = []
    raw_data = collect_agent_data(space, agent_portrayal)
    
    # Early exit if no agents
    if len(raw_data["loc"]) == 0:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)
    
    # Convert raw_data (dict of arrays) to Altair format (list of dicts)
    all_agent_data = []
    for i in range(len(raw_data["loc"])):
        agent_dict = {
            "x": float(raw_data["loc"][i][0]),
            "y": float(raw_data["loc"][i][1]),
            "color": raw_data["c"][i],
            "size": raw_data["s"][i]
        }
        # Add other properties if they exist
        if len(raw_data["alpha"]) > i:
            agent_dict["alpha"] = raw_data["alpha"][i]
        if len(raw_data["edgecolors"]) > i:
            agent_dict["edgecolor"] = raw_data["edgecolors"][i]
        if len(raw_data["linewidths"]) > i:
            agent_dict["linewidth"] = raw_data["linewidths"][i]
            
        all_agent_data.append(agent_dict)

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
            "x",
            axis=alt.Axis(grid=True),
            type=x_y_type,
            scale=alt.Scale(domain=(0, space.width - 1)),
        ),
        y=alt.Y(
            "y",
            axis=alt.Axis(grid=True),
            type=x_y_type,
            scale=alt.Scale(domain=(0, space.height - 1)),
        ),
    )

    return chart


def _draw_hex_grid(space, agent_portrayal):
    """Create Altair visualization for Hex Grid."""
    # Parameters for hexagon grid
    size = 1.0
    x_spacing = np.sqrt(3) * size
    y_spacing = 1.5 * size

    # Get color and size defaults
    s_default = (180 / max(space.width, space.height)) ** 2
    
    # Get agent data using the collect_agent_data helper function
    raw_data = collect_agent_data(space, agent_portrayal)
    
    # Early exit if no agents
    if len(raw_data["loc"]) == 0:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)
    
    # Transform hex coordinates to pixel coordinates
    loc = raw_data["loc"].astype(float)
    if loc.size > 0:
        # Apply the hex grid transformation for agent positions
        loc[:, 0] = loc[:, 0] * x_spacing + ((loc[:, 1] % 2) * (x_spacing / 2))
        loc[:, 1] = loc[:, 1] * y_spacing
        
    # Convert raw_data to Altair format
    all_agent_data = []
    for i in range(len(raw_data["loc"])):
        agent_dict = {
            "x": float(loc[i][0]),  # Use transformed coordinates
            "y": float(loc[i][1]),  # Use transformed coordinates
            "color": raw_data["c"][i],
            "size": raw_data["s"][i]
        }
        # Add other properties if they exist
        if len(raw_data["alpha"]) > i:
            agent_dict["alpha"] = raw_data["alpha"][i]
        if len(raw_data["edgecolors"]) > i:
            agent_dict["edgecolor"] = raw_data["edgecolors"][i]
        if len(raw_data["linewidths"]) > i:
            agent_dict["linewidth"] = raw_data["linewidths"][i]
            
        all_agent_data.append(agent_dict)
    
    # Calculate bounds
    x_max = space.width * x_spacing + (space.height % 2) * (x_spacing / 2)
    y_max = space.height * y_spacing
    x_padding = size * math.sqrt(3) / 2
    y_padding = size

    # Get hex grid lines using our new function
    hex_lines = _get_hexmesh_altair(space.width, space.height, size)

    # Create grid lines layer
    grid_lines = (
        alt.Chart(alt.Data(values=hex_lines))
        .mark_rule(color="gray", strokeWidth=1, opacity=0.5)
        .encode(x="x1:Q", y="y1:Q", x2="x2:Q", y2="y2:Q")
        .properties(width=280, height=280)
    )

    if not all_agent_data:
        return grid_lines

    # Create agent points layer
    agent_layer = alt.Chart(
        alt.Data(values=all_agent_data)
    ).mark_circle(
        filled=True
    ).encode(
        x=alt.X('x:Q', scale=alt.Scale(domain=[-x_padding, x_max + x_padding]),axis=alt.Axis(grid=False)),
        y=alt.Y('y:Q', scale=alt.Scale(domain=[-y_padding, y_max + y_padding]),axis=alt.Axis(grid=False)),
    ).properties(
        width=280,
        height=280
    )

    # Add color encoding if present
    if all_agent_data and "color" in all_agent_data[0]:
        agent_layer = agent_layer.encode(color=alt.Color("color:N"))

    # Add size encoding if present
    if all_agent_data and "size" in all_agent_data[0]:
        agent_layer = agent_layer.encode(size=alt.Size("size:Q"))
    else:
        agent_layer = agent_layer.mark_circle(filled=True, size=s_default)

    # Layer grid and agents together
    chart = (grid_lines + agent_layer).resolve_scale(
        x='shared',
        y='shared'
    )
    
    return chart


def _draw_network_grid(
    space: NetworkGrid | mesa.discrete_space.network.Network,
    agent_portrayal: Callable,
    draw_grid: bool = True,
    layout_alg=nx.spring_layout,
    layout_kwargs=None,
    **kwargs,
):
    """Create Altair visualization for Network Grid.
    
    Args:
        space: The network space to visualize
        agent_portrayal: A callable that defines how agents are portrayed
        draw_grid: Whether to draw the network edges
        layout_alg: A NetworkX layout algorithm to position nodes
        layout_kwargs: Arguments to pass to the layout algorithm
    """
    if layout_kwargs is None:
        layout_kwargs = {"seed": 0}
        
    # Get the graph and calculate positions using layout algorithm
    graph = space.G
    pos = layout_alg(graph, **layout_kwargs)
    
    # Calculate bounds with padding
    x_values = [p[0] for p in pos.values()]
    y_values = [p[1] for p in pos.values()]
    xmin, xmax = min(x_values), max(x_values)
    ymin, ymax = min(y_values), max(y_values)
    
    width = xmax - xmin
    height = ymax - ymin
    x_padding = width / 20
    y_padding = height / 20
    
    # Gather agent data using positions from layout algorithm
    s_default = (180 / max(width, height)) ** 2
    raw_data = collect_agent_data(space, agent_portrayal)
    
    # Early exit if no agents
    if len(raw_data["loc"]) == 0:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)
    
    # Map agent positions to layout positions
    loc = raw_data["loc"]
    positions = np.array([pos[node_id] for node_id in loc])
    
    # Create agent data for Altair
    all_agent_data = []
    for i in range(len(loc)):
        agent_dict = {
            "x": float(positions[i][0]),
            "y": float(positions[i][1]),
            "color": raw_data["c"][i],
            "size": raw_data["s"][i],
            "node_id": int(loc[i]) # Keep node ID for reference
        }
        # Add other properties if they exist
        if len(raw_data["alpha"]) > i:
            agent_dict["alpha"] = raw_data["alpha"][i]
        if len(raw_data["edgecolors"]) > i:
            agent_dict["edgecolor"] = raw_data["edgecolors"][i]
        if len(raw_data["linewidths"]) > i:
            agent_dict["linewidth"] = raw_data["linewidths"][i]
            
        all_agent_data.append(agent_dict)
     
    # Create edge data for drawing network connections
    edge_data = []
    if draw_grid:
        for u, v in graph.edges():
            edge_data.append({
                "x1": pos[u][0], 
                "y1": pos[u][1],
                "x2": pos[v][0], 
                "y2": pos[v][1]
            })
    
    # Create base chart for agents
    agent_chart = alt.Chart(
        alt.Data(values=all_agent_data)
    ).mark_circle(
        filled=True
    ).encode(
        x=alt.X('x:Q', scale=alt.Scale(domain=[xmin - x_padding, xmax + x_padding]), axis=alt.Axis(grid=False)),
        y=alt.Y('y:Q', scale=alt.Scale(domain=[ymin - y_padding, ymax + y_padding]),axis=alt.Axis(grid=False)),
    ).properties(
        width=280,
        height=280
    )
    
    # Add color and size encodings if present
    if all_agent_data:
        if "color" in all_agent_data[0]:
            agent_chart = agent_chart.encode(color=alt.Color("color:N"))
        
        if "size" in all_agent_data[0]:
            agent_chart = agent_chart.encode(size=alt.Size("size:Q"))
        else:
            agent_chart = agent_chart.mark_circle(filled=True, size=s_default)
    
    # Create edge chart
    if draw_grid and edge_data:
        edge_chart = alt.Chart(
            alt.Data(values=edge_data)
        ).mark_rule(
            color='gray',
            strokeDash=[5, 5],  # Equivalent to "--" style in matplotlib
            opacity=0.5,
            strokeWidth=1
        ).encode(
            x="x1:Q",
            y="y1:Q",
            x2="x2:Q",
            y2="y2:Q"
        )
        
        # Combine edge and agent charts
        return alt.layer(edge_chart, agent_chart)
    
    return agent_chart


def _draw_continuous_space(space, agent_portrayal):
    """Create Altair visualization for Continuous Space."""
    all_agent_data = []
    # Get agent data using the collect_agent_data helper function
    raw_data = collect_agent_data(space, agent_portrayal)
    
    # Early exit if no agents
    if len(raw_data["loc"]) == 0:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)
    
    # Convert raw_data (dict of arrays) to Altair format (list of dicts)
    all_agent_data = []
    for i in range(len(raw_data["loc"])):
        agent_dict = {
            "x": float(raw_data["loc"][i][0]),
            "y": float(raw_data["loc"][i][1]),
            "color": raw_data["c"][i],
            "size": raw_data["s"][i]
        }
        # Add other properties if they exist
        if len(raw_data["alpha"]) > i:
            agent_dict["alpha"] = raw_data["alpha"][i]
        if len(raw_data["edgecolors"]) > i:
            agent_dict["edgecolor"] = raw_data["edgecolors"][i]
        if len(raw_data["linewidths"]) > i:
            agent_dict["linewidth"] = raw_data["linewidths"][i]
            
        all_agent_data.append(agent_dict)
    if not all_agent_data:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)

    base = alt.Chart(alt.Data(values=all_agent_data)).properties(width=280, height=280)

    encodings = {
        "x": alt.X(
            "x:Q",
            scale=alt.Scale(domain=[0, space.width]),
            axis=alt.Axis(grid=True),  # Enable grid
        ),
        "y": alt.Y(
            "y:Q",
            scale=alt.Scale(domain=[0, space.height]),
            axis=alt.Axis(grid=True),  # Enable grid
        ),
    }

    if "color" in all_agent_data[0]:
        encodings["color"] = alt.Color("color:N")

    if "size" in all_agent_data:
        encodings["size"] = alt.Size("size:Q")
    else:
        base = base.mark_point(size=100, filled=True)

    chart = base.encode(**encodings)

    return chart

@lru_cache(maxsize=1024, typed=True)
def _get_hexmesh_altair(width: int, height: int, size: float = 1.0) -> list[dict]:
    """Generate hexagon vertices for the mesh in altair format."""
    
    # Parameters for hexagon grid
    x_spacing = np.sqrt(3) * size
    y_spacing = 1.5 * size
    
    hex_lines = []
    
    # For flat-topped hexagons (note the orientation)
    vertices_offsets = [
        (0, -size),                    # top
        (0.5 * np.sqrt(3) * size, -0.5 * size),  # top right
        (0.5 * np.sqrt(3) * size, 0.5 * size),   # bottom right
        (0, size),                     # bottom
        (-0.5 * np.sqrt(3) * size, 0.5 * size),  # bottom left
        (-0.5 * np.sqrt(3) * size, -0.5 * size)  # top left
    ]
    
    for row in range(height):
        for col in range(width):
            # Calculate center position with offset for odd rows
            x_center = col * x_spacing
            if row % 2 == 1:  # Odd rows are offset
                x_center += x_spacing / 2
            y_center = row * y_spacing
            
            # Calculate vertices for this hexagon
            vertices = []
            for dx, dy in vertices_offsets:
                vertices.append((x_center + dx, y_center + dy))
            
            # Create line segments for the hexagon
            for i in range(6):
                x1, y1 = vertices[i]
                x2, y2 = vertices[(i+1) % 6]
                hex_lines.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2})
    
    return hex_lines
