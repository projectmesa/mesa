import contextlib
from typing import Optional

import pandas as pd
import solara

with contextlib.suppress(ImportError):
    import altair as alt

@solara.component
def SpaceAltair(model, agent_portrayal, dependencies: Optional[list[any]] = None):
    space = getattr(model, "grid", None)
    if space is None:
        # Sometimes the space is defined as model.space instead of model.grid
        space = model.space
    chart = _draw_grid(space, agent_portrayal)
    solara.FigureAltair(chart)


def _draw_grid(space, agent_portrayal):
    def portray(g):
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

    all_agent_data = portray(space)
    df = pd.DataFrame(all_agent_data)
    chart = (
        alt.Chart(df)
        .mark_point(filled=True)
        .encode(
            # no x-axis label
            x=alt.X("x", axis=None),
            # no y-axis label
            y=alt.Y("y", axis=None),
        )
        # .configure_view(strokeOpacity=0)  # hide grid/chart lines
    )

    has_color = hasattr(all_agent_data[0], "color")
    if has_color:
        chart = chart.encode(color=alt.Color("color"))

    has_size = hasattr(all_agent_data[0], "size")
    if has_size:
        chart = chart.encode(size=alt.Size("size"))

    return chart
