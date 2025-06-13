import warnings
from dataclasses import fields

import altair as alt
import numpy as np
import pandas as pd

import mesa
from mesa.discrete_space import (
    OrthogonalMooreGrid,
    OrthogonalVonNeumannGrid,
)
from mesa.space import (
    HexMultiGrid,
    HexSingleGrid,
    MultiGrid,
    NetworkGrid,
    SingleGrid,
)

# Type aliases
OrthogonalGrid = SingleGrid | MultiGrid | OrthogonalMooreGrid | OrthogonalVonNeumannGrid
HexGrid = HexSingleGrid | HexMultiGrid | mesa.discrete_space.HexGrid
Network = NetworkGrid | mesa.discrete_space.Network

from .abstract_renderer import AbstractRenderer


class AltairBackend(AbstractRenderer):
    """A renderer that uses Altair."""

    def initialize_canvas(self, **kwargs):
        self._canvas = (
            alt.Chart(pd.DataFrame()).mark_point().properties(width=450, height=350)
        )

    def draw_structure(self, **kwargs):
        self.space_mesh = self.space_drawer.draw_altair(**kwargs)
        return self.space_mesh

    def _collect_agent_data(self, agent_portrayal, default_size=None):
        from mesa.visualization.components import AgentPortrayalStyle

        arguments = {
            "loc": [],
            "size": [],
            "color": [],
            "shape": [],
            "order": [],
            "opacity": [],
            "stroke": [],
            "strokeWidth": [],
            "filled": [],
        }
        style_fields = {f.name: f.default for f in fields(AgentPortrayalStyle)}
        class_default_size = style_fields.get("size")
        marker_map = {
            "o": "circle",
            "s": "square",
            "D": "diamond",
            "^": "triangle-up",
            "v": "triangle-down",
            "<": "triangle-left",
            ">": "triangle-right",
            "+": "cross",
            "x": "cross",
        }

        for agent in self.space.agents:
            portray_input = agent_portrayal(agent)
            if isinstance(portray_input, dict):
                # Legacy dict support
                dict_data = portray_input.copy()
                agent_x, agent_y = self.get_agent_pos_func(agent, self.space)
                aps = AgentPortrayalStyle(
                    x=agent_x,
                    y=agent_y,
                    size=dict_data.pop("size", style_fields.get("size")),
                    color=dict_data.pop("color", style_fields.get("color")),
                    marker=dict_data.pop("marker", style_fields.get("marker")),
                    zorder=dict_data.pop("zorder", style_fields.get("zorder")),
                    alpha=dict_data.pop("alpha", style_fields.get("alpha")),
                    edgecolors=dict_data.pop("edgecolors", None),
                    linewidths=dict_data.pop(
                        "linewidths", style_fields.get("linewidths")
                    ),
                )
            else:
                aps = portray_input
            if aps.x is None and aps.y is None:
                aps.x, aps.y = self.get_agent_pos_func(agent, self.space)

            arguments["loc"].append((aps.x, aps.y))
            arguments["size"].append(aps.size or default_size or class_default_size)
            arguments["color"].append(aps.color)
            raw_marker = aps.marker or style_fields.get("marker")
            arguments["shape"].append(marker_map.get(raw_marker, "circle"))
            arguments["order"].append(aps.zorder)
            arguments["opacity"].append(aps.alpha)
            arguments["stroke"].append(aps.edgecolors)
            arguments["strokeWidth"].append(aps.linewidths)
            arguments["filled"].append(aps.edgecolors is not None)

        return {k: np.asarray(v) for k, v in arguments.items()}

    def draw_agents(self, agent_portrayal, **kwargs):
        arguments = self._collect_agent_data(
            agent_portrayal, self.space_drawer.s_default
        )
        if arguments["loc"].size == 0:
            return None
        arguments = self.map_coords_func(arguments)

        df = pd.DataFrame(
            {
                "x": arguments["loc"][:, 0],
                "y": arguments["loc"][:, 1],
                "size": arguments["size"],
                "shape": arguments["shape"],
                "opacity": arguments["opacity"],
                "strokeWidth": arguments["strokeWidth"],
                "original_color": arguments["color"],
                "is_filled": arguments["filled"],
                "original_stroke": arguments["stroke"],
            }
        )

        df["viz_fill_color"] = df.apply(
            lambda r: r.original_color if r.is_filled else None, axis=1
        )
        df["viz_stroke_color"] = df.apply(
            lambda r: r.original_stroke if r.is_filled else r.original_color, axis=1
        )

        xmin, xmax, ymin, ymax = self.space_drawer.get_viz_limits()
        unique_shapes = df["shape"].unique().tolist()

        chart = (
            alt.Chart(df)
            .mark_point()
            .encode(
                x=alt.X("x:Q", scale=alt.Scale(domain=[xmin, xmax])),
                y=alt.Y("y:Q", scale=alt.Scale(domain=[ymin, ymax])),
                size=alt.Size("size:Q", legend=None),
                shape=alt.Shape(
                    "shape:N",
                    scale=alt.Scale(domain=unique_shapes, range=unique_shapes),
                ),
                opacity=alt.Opacity("opacity:Q", scale=alt.Scale(domain=[0, 1])),
                fill=alt.Fill("viz_fill_color:N", scale=None),
                stroke=alt.Stroke("viz_stroke_color:N", scale=None),
                strokeWidth=alt.StrokeWidth("strokeWidth:Q"),
                tooltip=["x", "y"],
            )
            .properties(**kwargs)
        )
        self.agent_mesh = chart
        return self.agent_mesh

    def draw_propertylayer(self, propertylayer_portrayal, **kwargs):
        return (None, None)

    def render(self, agent_portrayal=None, propertylayer_portrayal=None, **kwargs):
        structure_kwargs = kwargs.pop("structure_kwargs", {})
        agent_kwargs = kwargs.pop("agent_kwargs", {})

        self.clear_meshes()  # Clear previous renders

        structure_chart = self.draw_structure(**structure_kwargs)
        agent_chart = (
            self.draw_agents(agent_portrayal, **agent_kwargs)
            if agent_portrayal
            else None
        )
        prop_chart, prop_cbar = (
            self.draw_propertylayer(propertylayer_portrayal)
            if propertylayer_portrayal
            else (None, None)
        )

        charts = [
            c for c in [structure_chart, prop_chart, agent_chart] if c is not None
        ]
        final_chart = alt.layer(*charts) if charts else self.canvas

        if prop_cbar:
            final_chart = alt.vconcat(final_chart, prop_cbar).configure_view(
                stroke=None
            )

        return final_chart

    @property
    def canvas(self):
        if self._canvas is None:
            self.initialize_canvas()
        # Combine all parts into a final chart
        charts = [
            c
            for c in [
                self.space_mesh,
                self.agent_mesh,
                (self.propertylayer_mesh or [None])[0],
            ]
            if c
        ]
        if not charts:
            return self._canvas

        main_spatial = alt.layer(*charts)
        prop_cbar = (self.propertylayer_mesh or [None, None])[1]

        if prop_cbar:
            return alt.vconcat(main_spatial, prop_cbar).configure_view(stroke=None)
        return main_spatial
