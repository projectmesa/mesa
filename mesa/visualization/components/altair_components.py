"""Altair based solara components for visualization mesa spaces."""

import warnings

import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import solara
from matplotlib.colors import to_rgb

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
        )
    has_size = "size" in all_agent_data[0]
    if has_size:
        encoding_dict["size"] = alt.Size("size", type="quantitative")

    agent_chart = (
        alt.Chart(
            alt.Data(values=all_agent_data), encoding=alt.Encoding(**encoding_dict)
        )
        .mark_point(filled=True)
        .properties(width=300, height=300)
    )

    # This is the default value for the marker size, which auto-scales according to the grid area.
    if not has_size:
        length = min(space.width, space.height)
        agent_chart = agent_chart.mark_point(size=30000 / length**2, filled=True)

    if propertylayer_portrayal is not None:
        chart_width = agent_chart.properties().width
        chart_height = agent_chart.properties().height
        chart = chart_property_layers(
            space=space,
            propertylayer_portrayal=propertylayer_portrayal,
            chart_width=chart_width,
            chart_height=chart_height,
        )
        chart = chart + agent_chart
    else:
        chart = agent_chart

    return chart


def chart_property_layers(space, propertylayer_portrayal, chart_width, chart_height):
    """Creates Property Layers in the Altair Components.

    Args:
        space: the ContinuousSpace instance
        propertylayer_portrayal:Dictionary of PropertyLayer portrayal specifications
        chart_width: width of the agent chart to maintain consistency with the property charts
        chart_height: height of the agent chart to maintain consistency with the property charts
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

        if (space.width, space.height) != data.shape:
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

        if "color" in portrayal:
            # any value less than vmin will be mapped to the color corresponding to vmin
            # any value more than vmax will be mapped to the color corresponding to vmax
            def apply_rgba(val, vmin=vmin, vmax=vmax, alpha=alpha, portrayal=portrayal):
                a = (val - vmin) / (vmax - vmin)
                a = max(0, min(a, 1))  # to ensure that a is between 0 and 1
                a *= alpha  # vmax will have an opacity corresponding to alpha
                rgb_color = to_rgb(portrayal["color"])
                r = int(rgb_color[0] * 255)
                g = int(rgb_color[1] * 255)
                b = int(rgb_color[2] * 255)

                return f"rgba({r}, {g}, {b}, {a:.2f})"

            df["color"] = df["value"].apply(apply_rgba)

            chart = (
                alt.Chart(df)
                .mark_rect()
                .encode(
                    x=alt.X("x:O", axis=None),
                    y=alt.Y("y:O", axis=None),
                    fill=alt.Fill("color:N", scale=None),
                )
                .properties(width=chart_width, height=chart_height, title=layer_name)
            )
            base = (base + chart) if base is not None else chart

            if colorbar:
                list_value = []
                list_color = []

                i = vmin

                while i <= vmax:
                    list_value.append(i)
                    list_color.append(apply_rgba(i))
                    i += 1

                if vmax not in list_value:
                    list_value.append(vmax)
                    list_color.append(apply_rgba(vmax))
                df_colorbar = pd.DataFrame(
                    {
                        "value": list_value,
                        "color": list_color,
                    }
                )

                x_values = np.array(df_colorbar["value"])
                rgba_colors = np.array(df_colorbar["color"])
                # Ensure rgba_colors is a 2D array
                if rgba_colors.ndim == 1:
                    rgba_colors = np.array(
                        [list(color) for color in rgba_colors]
                    )  # Convert tuples to a 2D array

                def parse_rgba(color_str):
                    if isinstance(color_str, str) and color_str.startswith("rgba"):
                        color_str = (
                            color_str.replace("rgba(", "").replace(")", "").split(",")
                        )
                        return np.array(
                            [
                                float(color_str[i]) / 255
                                if i < 3
                                else float(color_str[i])
                                for i in range(4)
                            ],
                            dtype=float,
                        )
                    return np.array(
                        color_str, dtype=float
                    )  # If already a tuple, convert to float

                # Convert color strings to RGBA tuples (ensures correct dtype)
                rgba_colors = np.array(
                    [parse_rgba(c) for c in df_colorbar["color"]], dtype=float
                )

                # Ensure rgba_colors is a 2D array with shape (n, 4)
                rgba_colors = np.array(rgba_colors).reshape(-1, 4)

                # Create an RGBA gradient image (256 steps for smooth transition)
                gradient = np.zeros((50, 256, 4))  # (Height, Width, RGBA)

                # Interpolate each channel (R, G, B, A) separately
                interp_r = np.interp(
                    np.linspace(0, 255, 256),
                    np.linspace(0, 255, len(rgba_colors)),
                    rgba_colors[:, 0],
                )
                interp_g = np.interp(
                    np.linspace(0, 255, 256),
                    np.linspace(0, 255, len(rgba_colors)),
                    rgba_colors[:, 1],
                )
                interp_b = np.interp(
                    np.linspace(0, 255, 256),
                    np.linspace(0, 255, len(rgba_colors)),
                    rgba_colors[:, 2],
                )
                interp_a = np.interp(
                    np.linspace(0, 255, 256),
                    np.linspace(0, 255, len(rgba_colors)),
                    rgba_colors[:, 3],
                )

                interp_colors = np.stack(
                    [interp_r, interp_g, interp_b, interp_a], axis=-1
                )
                gradient[:] = interp_colors
                fig, ax = plt.subplots(figsize=(6, 0.25), dpi=100)
                ax.imshow(
                    gradient,
                    aspect="auto",
                    extent=[x_values.min(), x_values.max(), 0, 1],
                )
                ax.set_yticks([])
                ax.set_xlabel(layer_name)
                ax.set_xticks(np.linspace(x_values.min(), x_values.max(), 11))
                plt.show()

        elif "colormap" in portrayal:
            cmap = portrayal.get("colormap", "viridis")
            cmap_scale = alt.Scale(scheme=cmap, domain=[vmin, vmax])

            chart = (
                alt.Chart(df)
                .mark_rect(opacity=alpha)
                .encode(
                    x=alt.X("x:O", axis=None),
                    y=alt.Y("y:O", axis=None),
                    color=alt.Color(
                        "value:Q",
                        scale=cmap_scale,
                        title=layer_name,
                        legend=alt.Legend(title=layer_name) if colorbar else None,
                    ),
                )
                .properties(width=chart_width, height=chart_height)
            )
            base = (base + chart) if base is not None else chart

        else:
            raise ValueError(
                f"PropertyLayer {layer_name} portrayal must include 'color' or 'colormap'."
            )
    return base
