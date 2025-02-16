"""Altair based solara components for visualization mesa spaces."""

import warnings

import altair as alt
import numpy as np
import pandas as pd
import solara
from matplotlib.colors import to_rgba

import mesa
from mesa.discrete_space import DiscreteSpace, Grid
from mesa.space import ContinuousSpace, PropertyLayer, _Grid
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
        propertylayer_portrayal: Dictionary of PropertyLayer portrayal specifications
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
        return SpaceAltair(
            model, agent_portrayal, propertylayer_portrayal, post_process=post_process
        )

    return MakeSpaceAltair


@solara.component
def SpaceAltair(
    model,
    agent_portrayal,
    propertylayer_portrayal,
    dependencies: list[any] | None = None,
    post_process=None,
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

    chart = _draw_grid(space, agent_portrayal, propertylayer_portrayal)
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


def _draw_grid(space, agent_portrayal, propertylayer_portrayal):
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
        unique_colors = list({agent["color"] for agent in all_agent_data})
        encoding_dict["color"] = alt.Color(
            "color:N",
            scale=alt.Scale(domain=unique_colors, range=unique_colors),
            legend=None,
        )
    has_size = "size" in all_agent_data[0]
    if has_size:
        encoding_dict["size"] = alt.Size("size", type="quantitative", legend=None)

    agent_chart = (
        alt.Chart(
            alt.Data(values=all_agent_data), encoding=alt.Encoding(**encoding_dict)
        )
        .mark_point(filled=True)
        .properties(width=300, height=300)
        # .configure_view(strokeOpacity=0)  # hide grid/chart lines
    )
    # This is the default value for the marker size, which auto-scales
    # according to the grid area.
    if not has_size:
        length = min(space.width, space.height)
        chart = agent_chart.mark_point(size=30000 / length**2, filled=True)

    if propertylayer_portrayal is not None:
        base_width = agent_chart.properties().width
        base_height = agent_chart.properties().height
        chart = chart_property_layers(
            space=space,
            propertylayer_portrayal=propertylayer_portrayal,
            base_width=base_width,
            base_height=base_height,
        )

    chart = chart + agent_chart
    return chart


def chart_property_layers(space, propertylayer_portrayal, base_width, base_height):
    """Creates Property Layers in the Altair Components.

    Args:
        space: the ContinuousSpace instance
        propertylayer_portrayal:Dictionary of PropertyLayer portrayal specifications
        base_width: width of the agent chart to maintain consistency with the property charts
        base_height: height of the agent chart to maintain consistency with the property charts
    Returns:
        Altair Chart
    """
    try:
        # old style spaces
        property_layers = space.properties
    except AttributeError:
        # new style spaces
        property_layers = space._mesa_property_layers
    base = None
    for layer_name, portrayal in propertylayer_portrayal.items():
        layer = property_layers.get(layer_name, None)
        if not isinstance(
            layer,
            PropertyLayer | mesa.discrete_space.property_layer.PropertyLayer,
        ):
            continue

        data = layer.data.astype(float) if layer.data.dtype == bool else layer.data

        if (space.width, space.height) is not data.shape:
            warnings.warn(
                f"Layer {layer_name} dimensions ({data.shape}) do not match space dimensions ({space.width}, {space.height}).",
                UserWarning,
                stacklevel=2,
            )
        alpha = portrayal.get("alpha", 1)
        vmin = portrayal.get("vmin", np.min(data))
        vmax = portrayal.get("vmax", np.max(data))
        colorbar = portrayal.get("colorbar", True)

        # Prepare data for Altair (convert 2D array to a long-form DataFrame)
        df = pd.DataFrame(
            {
                "x": np.repeat(np.arange(data.shape[0]), data.shape[1]),
                "y": np.tile(np.arange(data.shape[1]), data.shape[0]),
                "value": data.flatten(),
            }
        )

        # Add RGBA color if "color" is in portrayal
        if "color" in portrayal:
            df["color"] = df["value"].apply(
                lambda val,
                portrayal=portrayal,
                alpha=alpha: f"rgba({int(to_rgba(portrayal['color'], alpha=alpha)[0] * 255)}, {int(to_rgba(portrayal['color'], alpha=alpha)[1] * 255)}, {int(to_rgba(portrayal['color'], alpha=alpha)[2] * 255)}, {to_rgba(portrayal['color'], alpha=alpha)[3]:.2f})"
                if val > 0
                else "rgba(0, 0, 0, 0)"
            )
            chart = (
                alt.Chart(df)
                .mark_rect()
                .encode(
                    x=alt.X("x:O", axis=None),
                    y=alt.Y("y:O", axis=None),
                    color=alt.Color("color:N", legend=None),
                )
                .properties(width=base_width, height=base_height, title=layer_name)
            )
            base = (base + chart) if base is not None else chart
        # Add colormap if "colormap" is in portrayal
        elif "colormap" in portrayal:
            cmap = portrayal.get("colormap", "viridis")
            cmap_scale = alt.Scale(scheme=cmap, domain=[vmin, vmax])

            chart = (
                alt.Chart(df)
                .mark_rect()
                .encode(
                    x=alt.X("x:O", axis=None),
                    y=alt.Y("y:O", axis=None),
                    color=alt.Color(
                        "value:Q",
                        scale=cmap_scale,
                        title=layer_name if colorbar else None,
                    ),
                )
                .properties(width=base_width, height=base_height, title=layer_name)
            )
            base = (base + chart) if base is not None else chart

        else:
            raise ValueError(
                f"PropertyLayer {layer_name} portrayal must include 'color' or 'colormap'."
            )
    return chart
