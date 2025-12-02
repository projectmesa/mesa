"""Altair-specific icon rendering layer for Mesa visualizations.

Builds a layered chart with mark_point (for non-icon agents) and mark_image
(for icon agents), with optional culling for performance.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import altair as alt
import pandas as pd

if TYPE_CHECKING:
    from mesa.visualization.space_drawers import SpaceDrawer


def build_altair_agent_chart(
    arguments: dict[str, Any],
    space_drawer: SpaceDrawer,
    chart_width: int = 450,
    chart_height: int = 350,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    enable_culling: bool = True,
) -> alt.Chart:
    """Build layered Altair chart for agents with icon support.

    Args:
        arguments: Dictionary with agent data (loc, size, color, icon_rasters, etc.)
        space_drawer: SpaceDrawer instance for getting visualization limits
        chart_width: Chart width in pixels
        chart_height: Chart height in pixels
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        enable_culling: If True, skip off-screen agents for performance

    Returns:
        alt.Chart: Layered chart with icons and/or markers
    """
    if arguments["loc"].size == 0:
        return None

    # Extract data
    icon_rasters = arguments.get("icon_rasters", [])
    icon_names = arguments.get("icon_names", [])

    # Get space limits
    xmin, xmax, ymin, ymax = space_drawer.get_viz_limits()

    # Prepare DataFrame
    df_data = {
        "x": arguments["loc"][:, 0],
        "y": arguments["loc"][:, 1],
        "size": arguments["size"],
        "shape": arguments.get("shape", ["circle"] * len(arguments["size"])),
        "opacity": arguments.get("opacity", [1.0] * len(arguments["size"])),
        "color": arguments.get("color", ["#1f77b4"] * len(arguments["size"])),
    }

    if icon_rasters:
        df_data["icon_url"] = icon_rasters
        df_data["icon_name"] = icon_names

    df = pd.DataFrame(df_data)

    # Optional culling: remove off-screen agents
    if enable_culling:
        # Add small margin for partially visible icons
        margin = 50  # pixels
        x_margin = (xmax - xmin) * margin / chart_width
        y_margin = (ymax - ymin) * margin / chart_height

        df = df[
            (df["x"] >= xmin - x_margin)
            & (df["x"] <= xmax + x_margin)
            & (df["y"] >= ymin - y_margin)
            & (df["y"] <= ymax + y_margin)
        ].copy()

    if df.empty:
        return None

    # Split into icon and non-icon agents
    has_icons = "icon_url" in df.columns
    if has_icons:
        df_icons = df[df["icon_url"].notna()].copy()
        df_points = df[df["icon_url"].isna()].copy()
    else:
        df_icons = pd.DataFrame()
        df_points = df.copy()

    layers = []
    tooltip_list = ["x", "y"]

    # Icon layer
    if not df_icons.empty:
        icon_chart = (
            alt.Chart(df_icons)
            .mark_image()
            .encode(
                x=alt.X(
                    "x:Q",
                    title=xlabel,
                    scale=alt.Scale(domain=[xmin, xmax]),
                    axis=None,
                ),
                y=alt.Y(
                    "y:Q",
                    title=ylabel,
                    scale=alt.Scale(domain=[ymin, ymax]),
                    axis=None,
                ),
                url="icon_url:N",
                size=alt.Size(
                    "size:Q",
                    legend=None,
                    scale=alt.Scale(range=[100, 2000]),  # Adjust for image sizing
                ),
                opacity=alt.Opacity(
                    "opacity:Q",
                    scale=alt.Scale(domain=[0, 1]),
                ),
                tooltip=tooltip_list,
            )
        )
        layers.append(icon_chart)

    # Point layer (fallback for non-icon agents)
    if not df_points.empty:
        point_chart = (
            alt.Chart(df_points)
            .mark_point(filled=True)
            .encode(
                x=alt.X(
                    "x:Q",
                    title=xlabel,
                    scale=alt.Scale(domain=[xmin, xmax]),
                    axis=None,
                ),
                y=alt.Y(
                    "y:Q",
                    title=ylabel,
                    scale=alt.Scale(domain=[ymin, ymax]),
                    axis=None,
                ),
                size=alt.Size("size:Q", legend=None, scale=alt.Scale(domain=[0, 50])),
                shape=alt.Shape("shape:N"),
                color=alt.Color("color:N", scale=None),
                opacity=alt.Opacity(
                    "opacity:Q",
                    scale=alt.Scale(domain=[0, 1]),
                ),
                tooltip=tooltip_list,
            )
        )
        layers.append(point_chart)

    # Combine layers
    if not layers:
        return None
    chart = layers[0] if len(layers) == 1 else alt.layer(*layers)

    chart = chart.properties(
        title=title,
        width=chart_width,
        height=chart_height,
    )

    return chart


"""Helper for building Altair icon layers with cached rasterization."""

if TYPE_CHECKING:
    from mesa.visualization.icon_cache import IconCache


def build_icon_layer(
    df: pd.DataFrame,
    icon_cache: IconCache,
    x_col: str = "x",
    y_col: str = "y",
    icon_col: str = "icon",
    size_col: str = "icon_size",
    **chart_kwargs,
) -> alt.Chart | None:
    """Build an Altair chart layer for icon-based agents.

    Args:
        df: DataFrame with agent data
        icon_cache: IconCache instance for rasterizing icons
        x_col: Column name for x coordinates
        y_col: Column name for y coordinates
        icon_col: Column name for icon names
        size_col: Column name for icon sizes
        **chart_kwargs: Additional kwargs for chart.properties()

    Returns:
        Altair Chart with mark_image layers, or None if no valid icons
    """
    if df.empty or icon_col not in df.columns:
        return None

    # Group by (icon_name, size) to minimize rasterization calls
    grouped = df.groupby([icon_col, size_col], dropna=True)
    layers = []

    for (icon_name, icon_size), group_df in grouped:
        if pd.isna(icon_name):
            continue

        data_url = icon_cache.get_or_create(icon_name, int(icon_size))
        if not data_url:
            continue

        # Assign the data URL to all rows in this group
        group_df_with_url = group_df.copy()
        group_df_with_url["_icon_url"] = data_url

        layer = (
            alt.Chart(group_df_with_url)
            .mark_image()
            .encode(
                x=alt.X(f"{x_col}:Q"),
                y=alt.Y(f"{y_col}:Q"),
                url=alt.Url("_icon_url:N"),
            )
        )
        layers.append(layer)

    if not layers:
        return None

    # Use ternary operator as suggested by ruff SIM108
    chart = layers[0] if len(layers) == 1 else alt.layer(*layers)

    chart = chart.properties(
        width=chart_kwargs.get("width", 500),
        height=chart_kwargs.get("height", 500),
    )

    return chart
