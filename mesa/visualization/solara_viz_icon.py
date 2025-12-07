"""Grid-based icon rendering demo for Mesa visualization.

This module provides an interactive demo showcasing icon-based agent
rendering on a discrete grid, similar to cellular automata visualizations.

Usage:
    Run as a standalone Solara app:
        $ solara run solara_viz_icon.py
"""

from __future__ import annotations

import time

import altair as alt
import numpy as np
import pandas as pd
import solara

from mesa.visualization.icon_cache import IconCache


class _GridAgent:
    """Agent that occupies a grid cell with a state."""

    def __init__(self, x: int, y: int, state: str):
        """Initialize grid agent.

        Args:
            x: X coordinate (column)
            y: Y coordinate (row)
            state: Agent state ("happy", "sad", "neutral")
        """
        self.pos = (x, y)
        self.state = state


class _GridSpace:
    """Discrete grid space containing agents."""

    def __init__(self, width: int, height: int, agents: list[_GridAgent]):
        """Initialize grid space.

        Args:
            width: Grid width (columns)
            height: Grid height (rows)
            agents: List of agents to place
        """
        self.width = width
        self.height = height
        self.agents = agents


def agent_portrayal(agent: _GridAgent, icon_size: int = 24) -> dict:
    """Return portrayal dict for an agent.

    Args:
        agent: The agent to portray
        icon_size: Size of the icon in pixels

    Returns:
        Dictionary with icon and color information
    """
    icon_map = {
        "happy": "smiley",
        "sad": "sad_face",
        "neutral": "neutral_face",
    }
    color_map = {
        "happy": "#4CAF50",  # Green
        "sad": "#753630",  # Brown
        "neutral": "#FFC107",  # Yellow
    }
    return {
        "icon": icon_map.get(agent.state),
        "icon_size": icon_size,
        "color": color_map.get(agent.state, "#808080"),
    }


@solara.component
def GridIconsDemo():
    """Main demo component for grid-based icon visualization."""
    # Reactive state
    grid_size = solara.use_reactive(15)
    agent_density = solara.use_reactive(0.3)
    icon_size = solara.use_reactive(24)
    show_grid_lines = solara.use_reactive(True)
    seed = solara.use_reactive(42)

    # Icon cache
    icon_cache = solara.use_memo(lambda: IconCache(backend="altair"), dependencies=[])

    # Generate grid and agents
    def generate_grid():
        rng = np.random.default_rng(seed.value)
        width = height = grid_size.value

        agents = []
        states = ["happy", "sad", "neutral"]

        for y in range(height):
            for x in range(width):
                if rng.random() < agent_density.value:
                    state = rng.choice(states)
                    agents.append(_GridAgent(x, y, state))

        return _GridSpace(width, height, agents)

    space = solara.use_memo(
        generate_grid, dependencies=[grid_size.value, agent_density.value, seed.value]
    )

    # Build the chart
    def create_chart():
        t0 = time.perf_counter()

        width = height = grid_size.value
        chart_size = 600
        cell_size = chart_size / grid_size.value

        layers = []

        # Layer 1: Background grid cells
        bg_data = []
        for y in range(height):
            for x in range(width):
                bg_data.append({"x": x, "y": y, "color": "#E8E8E8"})

        bg_df = pd.DataFrame(bg_data)

        bg_layer = (
            alt.Chart(bg_df)
            .mark_rect(
                stroke="#CCCCCC" if show_grid_lines.value else None, strokeWidth=0.5
            )
            .encode(
                x=alt.X("x:O", axis=None),
                y=alt.Y("y:O", axis=None, sort="descending"),
                color=alt.Color("color:N", scale=None),
            )
            .properties(
                width=chart_size,
                height=chart_size,
            )
        )
        layers.append(bg_layer)

        # Layer 2: Cell background colors based on agent state
        if space.agents:
            cell_data = []
            for agent in space.agents:
                x, y = agent.pos
                portrayal = agent_portrayal(agent, icon_size.value)
                cell_data.append(
                    {"x": x, "y": y, "color": portrayal["color"], "state": agent.state}
                )

            cell_df = pd.DataFrame(cell_data)

            cell_layer = (
                alt.Chart(cell_df)
                .mark_rect(
                    stroke="#CCCCCC" if show_grid_lines.value else None, strokeWidth=0.5
                )
                .encode(
                    x=alt.X("x:O", axis=None),
                    y=alt.Y("y:O", axis=None, sort="descending"),
                    color=alt.Color("color:N", scale=None),
                    tooltip=["x", "y", "state"],
                )
            )
            layers.append(cell_layer)

        # Layer 3: Icons on top of cells
        if space.agents:
            icon_data = []
            for agent in space.agents:
                x, y = agent.pos
                portrayal = agent_portrayal(agent, icon_size.value)
                icon_name = portrayal.get("icon")

                if icon_name:
                    icon_url = icon_cache.get_or_create(icon_name, icon_size.value)
                    if icon_url:
                        icon_data.append(
                            {"x": x, "y": y, "icon_url": icon_url, "state": agent.state}
                        )

            if icon_data:
                icon_df = pd.DataFrame(icon_data)

                icon_layer = (
                    alt.Chart(icon_df)
                    .mark_image(
                        width=cell_size * 0.8,
                        height=cell_size * 0.8,
                    )
                    .encode(
                        x=alt.X("x:O", axis=None),
                        y=alt.Y("y:O", axis=None, sort="descending"),
                        url="icon_url:N",
                        tooltip=["x", "y", "state"],
                    )
                )
                layers.append(icon_layer)

        chart = alt.layer(*layers).configure_view(strokeWidth=0)

        t1 = time.perf_counter()
        return chart, (t1 - t0) * 1000.0

    chart, render_time = solara.use_memo(
        create_chart,
        dependencies=[
            grid_size.value,
            agent_density.value,
            icon_size.value,
            show_grid_lines.value,
            seed.value,
        ],
    )

    # Count agents by state
    state_counts = {"happy": 0, "sad": 0, "neutral": 0}
    for agent in space.agents:
        state_counts[agent.state] = state_counts.get(agent.state, 0) + 1

    # UI Layout with Sidebar
    with solara.Column() as main:
        # Sidebar with controls
        with solara.Sidebar():
            solara.Markdown("## Controls")

            solara.Markdown("### Grid Settings")
            solara.SliderInt(
                "Grid Size",
                value=grid_size,
                min=5,
                max=25,
                step=1,
            )
            solara.SliderFloat(
                "Agent Density",
                value=agent_density,
                min=0.1,
                max=1.0,
                step=0.1,
            )
            solara.SliderInt(
                "Icon Size (px)",
                value=icon_size,
                min=16,
                max=48,
                step=4,
            )
            solara.Checkbox(
                label="Show grid lines",
                value=show_grid_lines,
            )
            solara.SliderInt(
                "Random Seed",
                value=seed,
                min=1,
                max=100,
            )

            solara.Markdown("---")
            solara.Markdown("### Statistics")
            solara.Markdown(f"**Grid:** {grid_size.value} x {grid_size.value}")
            solara.Markdown(f"**Total Cells:** {grid_size.value**2}")
            solara.Markdown(f"**Agents:** {len(space.agents)}")
            solara.Markdown("---")
            solara.Markdown(f"Happy: {state_counts['happy']}")
            solara.Markdown(f"Sad: {state_counts['sad']}")
            solara.Markdown(f"Neutral: {state_counts['neutral']}")
            solara.Markdown("---")
            solara.Markdown(f" **Render:** {render_time:.2f} ms")

        # Main content area
        solara.Markdown("<h1> Mesa Icon Grid Demo</h1>")
        solara.Markdown(
            "Each cell displays an agent with a smiley, sad, or neutral face icon."
        )

        # Align chart to the left
        with solara.Row(style={"justify-content": "center"}):
            if chart is not None:
                solara.FigureAltair(chart)
            else:
                solara.Warning("No chart available")

    return main


@solara.component
def Page():
    """Entry point for Solara app."""
    GridIconsDemo()
