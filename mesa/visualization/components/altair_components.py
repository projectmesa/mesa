"""Altair based solara components for visualization mesa spaces."""

import warnings

import altair as alt
import solara

from mesa.experimental.cell_space import DiscreteSpace, Grid
from mesa.space import ContinuousSpace, _Grid
from mesa.visualization.utils import update_counter


def make_space_altair(*args, **kwargs):  # noqa: D103
    warnings.warn(
        "make_space_altair has been renamed to make_altair_space",
        DeprecationWarning,
        stacklevel=2,
    )
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
        function: A function that creates a SpaceMatplotlib component
    """
    if agent_portrayal is None:

        def agent_portrayal(a):
            return {"id": a.unique_id}

    def MakeSpaceAltair(model):
        return SpaceAltair(model, agent_portrayal, post_process=post_process)

    return MakeSpaceAltair


@solara.component
def SpaceAltair(
    model, agent_portrayal, dependencies: list[any] | None = None, post_process=None
):
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
    # Apply post-processing if provided
    if post_process is not None:
        chart = post_process(chart)
    solara.FigureAltair(chart)


def _get_agent_data_old__discrete_space(space, agent_portrayal):
    """Format agent portrayal data for old-style discrete spaces.

    Args:
        space: the mesa.space._Grid instance
        agent_portrayal: the agent portrayal callable

    Returns:
        list of dicts

    """
    all_agent_data = []
    for content, (x, y) in space.coord_iter():
        if not content:
            continue
        if not hasattr(content, "__iter__"):
            # Is a single grid
            content = [content]  # noqa: PLW2901
        for agent in content:
            # use all data from agent portrayal, and add x,y coordinates
            agent_data = agent_portrayal(agent)
            agent_data["x"] = x
            agent_data["y"] = y
            all_agent_data.append(agent_data)
    return all_agent_data


def _get_agent_data_new_discrete_space(space: DiscreteSpace, agent_portrayal):
    """Format agent portrayal data for new-style discrete spaces.

    Args:
        space: the mesa.experiment.cell_space.Grid instance
        agent_portrayal: the agent portrayal callable

    Returns:
        list of dicts

    """
    all_agent_data = []

    for cell in space.all_cells:
        for agent in cell.agents:
            agent_data = agent_portrayal(agent)
            agent_data["x"] = cell.coordinate[0]
            agent_data["y"] = cell.coordinate[1]
            all_agent_data.append(agent_data)
    return all_agent_data


def _get_agent_data_continuous_space(space: ContinuousSpace, agent_portrayal):
    """Format agent portrayal data for continuous space.

    Args:
        space: the ContinuousSpace instance
        agent_portrayal: the agent portrayal callable

    Returns:
        list of dicts
    """
    all_agent_data = []
    for agent in space._agent_to_index:
        agent_data = agent_portrayal(agent)
        agent_data["x"] = agent.pos[0]
        agent_data["y"] = agent.pos[1]
        all_agent_data.append(agent_data)
    return all_agent_data


def _draw_grid(space, agent_portrayal):
    match space:
        case Grid():
            all_agent_data = _get_agent_data_new_discrete_space(space, agent_portrayal)
        case _Grid():
            all_agent_data = _get_agent_data_old__discrete_space(space, agent_portrayal)
        case ContinuousSpace():
            all_agent_data = _get_agent_data_continuous_space(space, agent_portrayal)
        case _:
            raise NotImplementedError(
                f"visualizing {type(space)} is currently not supported through altair"
            )

    invalid_tooltips = ["color", "size", "x", "y"]

    x_y_type = "ordinal" if not isinstance(space, ContinuousSpace) else "nominal"

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
    if not has_size:
        length = min(space.width, space.height)
        chart = chart.mark_point(size=30000 / length**2, filled=True)

    return chart
