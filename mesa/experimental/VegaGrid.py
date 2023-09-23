import json

import altair as alt
import solara


def get_agent_data_from_coord_iter(data):
    for agent, (x, y) in data:
        if agent:
            agent_data = json.loads(
                json.dumps(agent.__dict__, skipkeys=True, default=str)
            )
            agent_data["x"] = x
            agent_data["y"] = y
            agent_data.pop("model", None)
            agent_data.pop("pos", None)
            yield agent_data


def make_vega_grid(color=None, click_handler=None):
    return lambda model, _: VegaGrid(model, _, color, click_handler)


def VegaGrid(model, _agent_portrayal, color=None, on_click=None):
    if color is None:
        color = "unique_id:N"

    data = solara.reactive(
        list(get_agent_data_from_coord_iter(model.grid.coord_iter()))
    )

    def update_data():
        data.value = list(get_agent_data_from_coord_iter(model.grid.coord_iter()))

    def click_handler(datum):
        if datum is None:
            return
        agent = model.schedule._agents[tuple(datum["unique_id"])]
        on_click(agent)
        update_data()

    default_tooltip = [f"{key}:N" for key in data.value[0]]
    chart = (
        alt.Chart(alt.Data(values=data.value))
        .mark_rect()
        .encode(
            x=alt.X("x:N", scale=alt.Scale(domain=list(range(model.grid.width)))),
            y=alt.Y(
                "y:N",
                scale=alt.Scale(domain=list(range(model.grid.height - 1, -1, -1))),
            ),
            color=color,
            tooltip=default_tooltip,
        )
    )
    return solara.FigureAltair(chart, on_click=click_handler)
