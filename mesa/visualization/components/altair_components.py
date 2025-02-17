"""Altair based solara components for visualization mesa spaces."""

import contextlib
import math
import warnings
from collections.abc import Callable

import solara

import mesa
import mesa.experimental
from mesa.experimental.cell_space import HexGrid

with contextlib.suppress(ImportError):
    import altair as alt

from mesa.experimental.cell_space import Grid
from mesa.space import ContinuousSpace, NetworkGrid, _Grid
from mesa.visualization.utils import update_counter


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
    update_counter.get()
    space = getattr(model, "grid", None)
    if space is None:
        # Sometimes the space is defined as model.space instead of model.grid
        space = model.space

    chart = _draw_grid(space, agent_portrayal)
    # Apply post-processing if provided
    if post_process is not None:
        chart = post_process(chart)

    solara.FigureAltair(chart)


def axial_to_pixel(q, r, size=1):
    """Convert axial coordinates (q, r) to pixel coordinates for hexagonal grid."""
    x = size * math.sqrt(3) * (q + r / 2)
    y = size * 1.5 * r
    return x, y


def get_agent_data(space, agent_portrayal):
    """Generic method to extract agent data for visualization across all space types.

    Args:
        space: Mesa space object
        agent_portrayal: Function defining agent visualization properties

    Returns:
        List of agent data dictionaries with coordinates
    """
    all_agent_data = []

    match space:
        case Grid():
            # New DiscreteSpace or experimental cell space
            for cell in space.all_cells:
                for agent in cell.agents:
                    data = agent_portrayal(agent)
                    data.update({"x": cell.coordinate[0], "y": cell.coordinate[1]})
                    all_agent_data.append(data)

        case _Grid():
            # Legacy Grid
            for content, (x, y) in space.coord_iter():
                if not content:
                    continue
                agents = [content] if not hasattr(content, "__iter__") else content
                for agent in agents:
                    data = agent_portrayal(agent)
                    data.update({"x": x, "y": y})
                    all_agent_data.append(data)

        case HexGrid():
            # Hex-based grid
            for content, (q, r) in space.coord_iter():
                if content:
                    for agent in content:
                        data = agent_portrayal(agent)
                        data.update({"q": q, "r": r})  # Store axial coordinates
                        all_agent_data.append(data)

        case NetworkGrid():
            # Network grid
            for node in space.G.nodes():
                agents = space.G.nodes[node].get("agent", [])
                if not isinstance(agents, list):
                    agents = [agents] if agents else []

                for agent in agents:
                    if agent:
                        data = agent_portrayal(agent)
                        data.update({"node": node})  # Store node information
                        all_agent_data.append(data)

        case ContinuousSpace() | mesa.experimental.continuous_space.ContinuousSpace():
            # Continuous space
            for agent in space.agents:
                data = agent_portrayal(agent)
                data.update({"x": agent.pos[0], "y": agent.pos[1]})
                all_agent_data.append(data)

        case _:
            raise NotImplementedError(f"Unsupported space type: {type(space)}")

    return all_agent_data


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
    all_agent_data = get_agent_data(space, agent_portrayal)

    # Handle empty state
    if not all_agent_data:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)

    match space:
        case Grid():
            return _draw_discrete_grid(space, all_agent_data, agent_portrayal)
        case _Grid():
            return _draw_legacy_grid(space, all_agent_data, agent_portrayal)
        case HexGrid():
            return _draw_hex_grid(space, all_agent_data, agent_portrayal)
        case NetworkGrid():
            return _draw_network_grid(space, all_agent_data, agent_portrayal)
        case ContinuousSpace() | mesa.experimental.continuous_space.ContinuousSpace():
            return _draw_continuous_space(space, all_agent_data, agent_portrayal)
        case _:
            raise NotImplementedError(f"Unsupported space type: {type(space)}")


def _draw_discrete_grid(space, all_agent_data, agent_portrayal):
    """Create Altair visualization for Discrete Grid."""
    invalid_tooltips = ["color", "size", "x", "y"]
    x_y_type = "ordinal"

    encoding_dict = {
        "x": alt.X("x", axis=None, type=x_y_type),
        "y": alt.Y("y", axis=None, type=x_y_type),
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

    if not has_size:
        length = min(space.width, space.height)
        chart = chart.mark_point(size=30000 / length**2, filled=True)

    chart = chart.encode(
        x=alt.X(
            "x", axis=None, type=x_y_type, scale=alt.Scale(domain=(0, space.width - 1))
        ),
        y=alt.Y(
            "y", axis=None, type=x_y_type, scale=alt.Scale(domain=(0, space.height - 1))
        ),
    )

    return chart


def _draw_legacy_grid(space, all_agent_data, agent_portrayal):
    """Create Altair visualization for Legacy Grid."""
    invalid_tooltips = ["color", "size", "x", "y"]
    x_y_type = "ordinal"

    encoding_dict = {
        "x": alt.X("x", axis=None, type=x_y_type),
        "y": alt.Y("y", axis=None, type=x_y_type),
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

    if not has_size:
        length = min(space.width, space.height)
        chart = chart.mark_point(size=30000 / length**2, filled=True)

    chart = chart.encode(
        x=alt.X(
            "x", axis=None, type=x_y_type, scale=alt.Scale(domain=(0, space.width - 1))
        ),
        y=alt.Y(
            "y", axis=None, type=x_y_type, scale=alt.Scale(domain=(0, space.height - 1))
        ),
    )

    return chart


def _draw_hex_grid(space, all_agent_data, agent_portrayal):
    """Create Altair visualization for Hex Grid."""
    invalid_tooltips = ["color", "size", "x", "y", "q", "r"]
    x_y_type = "quantitative"

    # Parameters for hexagon grid
    size = 1.0
    x_spacing = math.sqrt(3) * size
    y_spacing = 1.5 * size

    # Calculate x, y coordinates from axial coordinates
    for agent_data in all_agent_data:
        q = agent_data.pop("q")
        r = agent_data.pop("r")
        x, y = axial_to_pixel(q, r)
        agent_data["x"] = x
        agent_data["y"] = y

    # Calculate proper bounds that account for the full hexagon width and height
    x_max = space.width * x_spacing + (space.height % 2) * (x_spacing / 2)
    y_max = space.height * y_spacing

    # Add padding that accounts for the hexagon points
    x_padding = size * math.sqrt(3) / 2
    y_padding = size

    x_scale = alt.Scale(domain=(-2 * x_padding, x_max + x_padding))
    y_scale = alt.Scale(domain=(-2 * y_padding, y_max + y_padding))

    encoding_dict = {
        "x": alt.X("x", axis=None, type=x_y_type, scale=x_scale),
        "y": alt.Y("y", axis=None, type=x_y_type, scale=y_scale),
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


def _draw_network_grid(space, all_agent_data, agent_portrayal):
    """Create Altair visualization for Network Grid."""
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
        "x": alt.X("x", axis=None, type=x_y_type, scale=x_scale),
        "y": alt.Y("y", axis=None, type=x_y_type, scale=y_scale),
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


def _draw_continuous_space(space, all_agent_data, agent_portrayal):
    """Create Altair visualization for Continuous Space."""
    invalid_tooltips = ["color", "size", "x", "y"]
    x_y_type = "quantitative"

    x_scale = alt.Scale(domain=(0, space.width))
    y_scale = alt.Scale(domain=(0, space.height))

    encoding_dict = {
        "x": alt.X("x", axis=None, type=x_y_type, scale=x_scale),
        "y": alt.Y("y", axis=None, type=x_y_type, scale=y_scale),
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
