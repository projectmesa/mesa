"""Altair based solara components for visualization mesa spaces."""

import contextlib

import solara

with contextlib.suppress(ImportError):
    import altair as alt

from mesa.experimental.cell_space import DiscreteSpace, Grid
from mesa.space import ContinuousSpace, _Grid
from mesa.visualization.utils import update_counter


def make_space_altair(agent_portrayal=None):  # noqa: D103
    if agent_portrayal is None:

        def agent_portrayal(a):
            return {"id": a.unique_id}

    def MakeSpaceAltair(model):
        return SpaceAltair(model, agent_portrayal)

    return MakeSpaceAltair


@solara.component
def SpaceAltair(model, agent_portrayal, dependencies: list[any] | None = None):  # noqa: D103
    update_counter.get()
    space = getattr(model, "grid", None)
    if space is None:
        # Sometimes the space is defined as model.space instead of model.grid
        space = model.space


    chart = _draw_grid(space, agent_portrayal)
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


def _get_agent_data_new_discrete_space(space:DiscreteSpace, agent_portrayal):
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


def _get_agent_data_continous_space(space:ContinuousSpace, agent_portrayal):
    """Format agent portrayal data for contiuous space.

    Args:
        space: the ContinuousSpace instance
        agent_portrayal: the agent portrayal callable

    Returns:
        list of dicts
    """
    data = space.__agent_points

    all_agent_data = []
    for i, agent in space._index_to_agent.items():
        agent_data = agent_portrayal(agent)
        agent_data["x"] = data[i, 0]
        agent_data["y"] = data[i, 1]
        all_agent_data.append(agent)
    return all_agent_data

def _draw_grid(space, agent_portrayal):

    match space:
        case Grid():
            all_agent_data = _get_agent_data_new_discrete_space(space, agent_portrayal)
        case _Grid():
            all_agent_data = _get_agent_data_old__discrete_space(space, agent_portrayal)
        case ContinuousSpace():
            all_agent_data = _get_agent_data_continous_space(space, agent_portrayal)
        case _:
            raise NotImplementedError(f"visualizing {type(space)} is currently not supported through altair")

    invalid_tooltips = ["color", "size", "x", "y"]

    encoding_dict = {
        # no x-axis label
        "x": alt.X("x", axis=None, type="ordinal"),
        # no y-axis label
        "y": alt.Y("y", axis=None, type="ordinal"),
        "tooltip": [
            alt.Tooltip(key, type=alt.utils.infer_vegalite_type([value]))
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
