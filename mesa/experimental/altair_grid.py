from typing import Callable, Optional

import altair as alt
import solara

import mesa


def get_agent_data_from_coord_iter(data):
    """
    Extracts agent data from a sequence of tuples containing agent objects and their coordinates.

    Parameters:
    - data (iterable): A sequence of tuples where each tuple contains an agent object and its coordinates.

    Yields:
    - dict: A dictionary containing agent data with updated coordinates. The dictionary excludes 'model' and 'pos' attributes.
    """
    for agent, (x, y) in data:
        if agent:
            agent_data = agent[0].__dict__.copy()
            agent_data.update({"x": x, "y": y})
            agent_data.pop("model", None)
            agent_data.pop("pos", None)
            yield agent_data


def create_grid(
    color: Optional[str] = None,
    on_click: Optional[Callable[[mesa.Model, mesa.space.Coordinate], None]] = None,
) -> Callable[[mesa.Model], solara.component]:
    """
    Factory function for creating a grid component for a Mesa model.

    Parameters:
    - color (Optional[str]): Color of the grid lines. Defaults to None.
    - on_click (Optional[Callable[[mesa.Model, mesa.space.Coordinate], None]]):
    Function to be called when a grid cell is clicked. Defaults to None.

    Returns:
    - Callable[[mesa.Model], solara.component]: A function that creates a grid component for the given model.
    """

    def create_grid_function(model: mesa.Model) -> solara.component:
        return Grid(model, color, on_click)

    return create_grid_function


def Grid(model, color=None, on_click=None):
    """
    Handles click events on grid cells.

    Parameters:
    - datum (dict): Data associated with the clicked cell.

    Notes:
    - Invokes the provided `on_click` function with the model and cell coordinates.
    - Updates the data displayed on the grid.
    """
    if color is None:
        color = "unique_id:N"

    if color[-2] != ":":
        color = color + ":N"

    print(model.grid.coord_iter())

    data = solara.reactive(
        list(get_agent_data_from_coord_iter(model.grid.coord_iter()))
    )

    def update_data():
        data.value = list(get_agent_data_from_coord_iter(model.grid.coord_iter()))

    def click_handler(datum):
        if datum is None:
            return
        on_click(model, datum["x"], datum["y"])
        update_data()

    default_tooltip = [
        f"{key}:N" for key in data.value[0]
    ]  # add all agent attributes to tooltip
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
        .properties(width=600, height=600)
    )
    return solara.FigureAltair(chart, on_click=click_handler)
