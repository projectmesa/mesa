"""Altair based solara components for visualization mesa spaces."""

import contextlib
import math
import warnings
from collections.abc import Callable

import solara

import mesa

with contextlib.suppress(ImportError):
    import altair as alt

from mesa.experimental.cell_space import Grid, HexGrid
from mesa.space import ContinuousSpace, NetworkGrid, _Grid
from mesa.visualization.utils import update_counter


def make_space_altair(*args, **kwargs):  # noqa: D103
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
        post_process :not yet implemented
        space_drawing_kwargs : not yet implemented

    ``agent_portrayal`` is called with an agent and should return a dict. Valid fields in this dict are "color",
    "size", "marker", and "zorder". Other field are ignored and will result in a user warning.

    Returns:
        function: A function that creates a SpaceMatplotlib component
    """
    if agent_portrayal is None:

        def agent_portrayal(a):
            return {"id": a.unique_id}

    def MakeSpaceAltair(model):
        return SpaceAltair(model, agent_portrayal)

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
    """Create an Altair plot for model."""
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
def SpaceAltair(model, agent_portrayal, dependencies: list[any] | None = None):
    """Create an Altair-based space visualization component.

    Returns:
        a solara FigureAltair instance
    """
    update_counter.get()
    space = getattr(model, "grid", None)
    if space is None:
        # Sometimes the space is defined as model.space instead of model.grid
        space = model.space

    chart = _draw_grid(space, agent_portrayal)
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

    # New DiscreteSpace
    if isinstance(space, Grid):
        for cell in space.all_cells:
            for agent in cell.agents:
                data = agent_portrayal(agent)
                data.update({"x": cell.coordinate[0], "y": cell.coordinate[1]})
                all_agent_data.append(data)

    # Legacy Grid
    elif isinstance(space, _Grid):
        for content, (x, y) in space.coord_iter():
            if not content:
                continue
            agents = [content] if not hasattr(content, "__iter__") else content
            for agent in agents:
                data = agent_portrayal(agent)
                data.update({"x": x, "y": y})
                all_agent_data.append(data)

    elif isinstance(space, HexGrid):
        for content, (q, r) in space.coord_iter():
            if content:
                for agent in content:
                    data = agent_portrayal(agent)
                    x, y = axial_to_pixel(q, r)
                    data.update({"x": x, "y": y})
                    all_agent_data.append(data)

    elif isinstance(space, NetworkGrid):
        for node in space.G.nodes():
            agents = space.G.nodes[node].get("agent", [])
            if isinstance(agents, list):
                agent_list = agents
            else:
                agent_list = [agents] if agents else []

            for agent in agent_list:
                if agent:
                    pos = space.G.nodes[node].get("pos", (0, 0))
                    data = agent_portrayal(agent)
                    data.update({"x": pos[0], "y": pos[1]})
                    all_agent_data.append(data)

    elif isinstance(
        space, ContinuousSpace | mesa.experimental.continuous_space.ContinuousSpace
    ):
        for agent in space.agents:
            data = agent_portrayal(agent)
            data.update({"x": agent.pos[0], "y": agent.pos[1]})
            all_agent_data.append(data)

    else:
        raise NotImplementedError(f"Unsupported space type: {type(space)}")

    return all_agent_data


def _draw_grid(space, agent_portrayal):
    """Create Altair visualization for any supported space type."""
    all_agent_data = get_agent_data(space, agent_portrayal)

    # Handle empty state
    if not all_agent_data:
        return alt.Chart().mark_text(text="No agents").properties(width=280, height=280)

    invalid_tooltips = ["color", "size", "x", "y"]

    x_y_type = (
        "quantitative"
        if isinstance(
            space,
            ContinuousSpace
            | HexGrid
            | NetworkGrid
            | mesa.experimental.continuous_space.ContinuousSpace,
        )
        else "ordinal"
    )

    encoding_dict = {
        # no x-axis label
        "x": alt.X("x", axis=None, type=x_y_type),
        # no y-axis label
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
        # .configure_view(strokeOpacity=0)  # hide grid/chart lines
    )
    # This is the default value for the marker size, which auto-scales
    # according to the grid area.
    if not has_size and isinstance(space, _Grid | Grid):
        length = min(space.width, space.height)
        chart = chart.mark_point(size=30000 / length**2, filled=True)

    return chart
