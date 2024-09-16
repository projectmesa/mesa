"""Altair components."""

import contextlib

import solara

with contextlib.suppress(ImportError):
    import altair as alt


@solara.component
def SpaceAltair(model, agent_portrayal, dependencies: list[any] | None = None):
    """A component that renders a Space using Altair.

    Args:
        model: a model instance
        agent_portrayal: agent portray specification
        dependencies: optional list of dependencies (currently not used)

    """
    space = getattr(model, "grid", None)
    if space is None:
        # Sometimes the space is defined as model.space instead of model.grid
        space = model.space
    chart = _draw_grid(space, agent_portrayal)
    solara.FigureAltair(chart)


def _draw_grid(space, agent_portrayal):
    def portray(g):
        all_agent_data = []
        for content, (x, y) in g.coord_iter():
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

    all_agent_data = portray(space)
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
