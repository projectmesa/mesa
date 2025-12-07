"""Test the backends of the visualization package."""

import types
from unittest.mock import MagicMock

import altair as alt
import numpy as np
import pytest

from mesa.discrete_space.grid import OrthogonalMooreGrid
from mesa.discrete_space.property_layer import PropertyLayer
from mesa.visualization.backends import AltairBackend, MatplotlibBackend
from mesa.visualization.components import AgentPortrayalStyle, PropertyLayerStyle


def test_matplotlib_initialize_canvas():
    """Test that MatplotlibBackend initializes canvas with ax and fig."""
    mb = MatplotlibBackend(space_drawer=MagicMock())
    mb.initialize_canvas()
    assert mb.ax is not None
    assert mb.fig is not None


def test_matplotlib_initialize_canvas_with_custom_ax():
    """Test initializing canvas with a provided ax skips creating fig."""
    mb = MatplotlibBackend(space_drawer=MagicMock())
    ax = MagicMock()
    mb.initialize_canvas(ax=ax)
    assert mb.ax == ax
    assert not hasattr(mb, "fig")


def test_matplotlib_backend_draw_structure(monkeypatch):
    """Test draw_structure returns ax from draw_matplotlib."""
    mb = MatplotlibBackend(space_drawer=MagicMock())
    mb.initialize_canvas()
    ax = MagicMock()
    monkeypatch.setattr(mb, "ax", ax)
    mb.space_drawer.draw_matplotlib = MagicMock(return_value=ax)
    assert mb.draw_structure() == ax


def test_matplotlib_backend_collects_agent_data():
    """Test collect_agent_data."""
    mb = MatplotlibBackend(space_drawer=MagicMock())

    class DummyAgent:
        pos = (0, 0)
        cell = types.SimpleNamespace(coordinate=(0, 0))

    class DummySpace:
        agents = [DummyAgent()]

    # Test with AgentPortrayalStyle
    def agent_portrayal_style(agent):
        return AgentPortrayalStyle(
            x=0,
            y=0,
            size=5,
            color="red",
            marker="o",
            zorder=1,
            alpha=1.0,
            edgecolors="black",
            linewidths=1,
        )

    data = mb.collect_agent_data(DummySpace(), agent_portrayal_style)
    assert "loc" in data and data["loc"].shape[0] == 1

    # Test with dict-based portrayal
    def agent_portrayal_dict(agent):
        return {"size": 5, "color": "red", "marker": "o"}

    data = mb.collect_agent_data(DummySpace(), agent_portrayal_dict)
    assert "loc" in data and data["loc"].shape[0] == 1


def test_matplotlib_backend_draw_agents():
    """Test drawing agents."""
    mb = MatplotlibBackend(space_drawer=MagicMock())
    mb.initialize_canvas()

    # Test with empty data
    arguments = {"loc": np.array([]), "marker": np.array([]), "zorder": np.array([])}
    result = mb.draw_agents(arguments)
    assert result is None

    # Test with data
    arguments = {
        "loc": np.array([[0, 0], [1, 1]]),
        "marker": np.array(["o", "s"]),
        "zorder": np.array([1, 1]),
        "s": np.array([5, 5]),
        "c": np.array(["red", "blue"]),
        "alpha": np.array([1.0, 1.0]),
        "edgecolors": np.array(["black", "black"]),
        "linewidths": np.array([1, 1]),
    }
    result = mb.draw_agents(arguments)
    assert result == mb.ax


def test_matplotlib_backend_draw_agents_bad_marker(monkeypatch):
    """Test drawing agents with nonexistent marker file raises ValueError."""
    mb = MatplotlibBackend(space_drawer=MagicMock())
    mb.initialize_canvas()
    monkeypatch.setattr("os.path.isfile", lambda path: False)
    arguments = {
        "loc": np.array([[0, 0]]),
        "marker": np.array(["notafile.png"], dtype=object),
        "zorder": np.array([1]),
        "s": np.array([1]),
        "c": np.array(["red"]),
        "alpha": np.array([1.0]),
        "edgecolors": np.array(["black"]),
        "linewidths": np.array([1]),
    }
    with pytest.raises(ValueError):
        mb.draw_agents(arguments.copy())


def test_matplotlib_backend_draw_propertylayer():
    """Test drawing property layer."""
    # Test with color
    mb = MatplotlibBackend(space_drawer=MagicMock())
    mb.initialize_canvas()

    # set up space and layer
    space = OrthogonalMooreGrid([2, 2])
    layer = PropertyLayer("test", [2, 2], default_value=0.0)
    space.add_property_layer(layer)

    # Test with color
    def propertylayer_portrayal_color(layer):
        return PropertyLayerStyle(
            color="red", alpha=0.5, vmin=0, vmax=1, colorbar=False
        )

    result = mb.draw_propertylayer(
        space, space._mesa_property_layers, propertylayer_portrayal_color
    )
    assert result[0] == mb.ax
    assert result[1] is None

    # Test with colormap
    def propertylayer_portrayal_colormap(layer):
        return PropertyLayerStyle(
            colormap="viridis", alpha=0.5, vmin=0, vmax=1, colorbar=True
        )

    result = mb.draw_propertylayer(
        space, space._mesa_property_layers, propertylayer_portrayal_colormap
    )
    assert result[0] == mb.ax
    assert result[1] is not None

    # Test with no color or colormap
    def propertylayer_portrayal_no_color_colormap(layer):
        return PropertyLayerStyle(
            color=None, colormap=None, alpha=1.0, vmin=0, vmax=1, colorbar=False
        )

    with pytest.raises(ValueError, match="Specify one of 'color' or 'colormap'"):
        mb.draw_propertylayer(
            space,
            space._mesa_property_layers,
            propertylayer_portrayal_no_color_colormap,
        )


def test_altair_backend_draw_structure():
    """Test AltairBackend draw_structure returns chart."""
    ab = AltairBackend(space_drawer=MagicMock())
    ab.space_drawer.draw_altair = MagicMock(return_value="chart")
    assert ab.draw_structure() == "chart"


def test_altair_backend_collects_agent_data():
    """Test collect_agent_data."""
    ab = AltairBackend(space_drawer=MagicMock())

    class DummyAgent:
        pos = (0, 0)
        cell = types.SimpleNamespace(coordinate=(0, 0))

    class DummySpace:
        agents = [DummyAgent()]

    # Test with AgentPortrayalStyle
    def agent_portrayal_style(agent):
        return AgentPortrayalStyle(
            x=0,
            y=0,
            size=5,
            color="red",
            marker="o",
            zorder=1,
            alpha=1.0,
            edgecolors="black",
            linewidths=1,
        )

    data = ab.collect_agent_data(DummySpace(), agent_portrayal_style)
    assert "loc" in data and data["loc"].shape[0] == 1

    # Test with dict-based portrayal
    def agent_portrayal_dict(agent):
        return {"size": 5, "color": "red", "marker": "o"}

    data = ab.collect_agent_data(DummySpace(), agent_portrayal_dict)
    assert "loc" in data and data["loc"].shape[0] == 1


def test_altair_backend_collects_agent_data_marker_mapping():
    """Test collect_agent_data maps markers to Altair shapes."""
    ab = AltairBackend(space_drawer=MagicMock())

    class DummyAgent:
        pos = (0, 0)
        cell = types.SimpleNamespace(coordinate=(0, 0))

    class DummySpace:
        agents = [DummyAgent()]

    def agent_portrayal(agent):
        return AgentPortrayalStyle(
            x=0, y=0, size=5, color="red", marker="s", zorder=1, alpha=1.0
        )

    data = ab.collect_agent_data(DummySpace(), agent_portrayal)
    assert data["shape"][0] == "square"


def test_altair_backend_draw_agents():
    """Test draw_agents."""
    # Test with empty data
    ab = AltairBackend(space_drawer=MagicMock())
    result = ab.draw_agents({"loc": np.array([])})
    assert result is None

    # Test with data
    arguments = {
        "loc": np.array([[0, 0], [1, 1]]),
        "size": np.array([5, 5]),
        "shape": np.array(["circle", "square"]),
        "opacity": np.array([1.0, 1.0]),
        "strokeWidth": np.array([1, 1]),
        "color": np.array(["red", "blue"]),
        "filled": np.array([True, True]),
        "stroke": np.array(["black", "black"]),
    }
    ab.space_drawer.get_viz_limits = MagicMock(return_value=(0, 10, 0, 10))
    assert ab.draw_agents(arguments) is not None


def test_altair_backend_draw_propertylayer():
    """Test drawing propertylayer."""
    ab = AltairBackend(space_drawer=MagicMock())

    # set up space and layer
    space = OrthogonalMooreGrid([2, 2])
    layer = PropertyLayer("test", [2, 2], default_value=0.0)
    space.add_property_layer(layer)

    # Test with color
    def propertylayer_portrayal_color(layer):
        return PropertyLayerStyle(
            color="red", alpha=0.5, vmin=0, vmax=1, colorbar=False
        )

    result = ab.draw_propertylayer(
        space, space._mesa_property_layers, propertylayer_portrayal_color
    )
    assert result is not None

    # Test with colormap
    def propertylayer_portrayal_colormap(layer):
        return PropertyLayerStyle(
            colormap="viridis", alpha=0.5, vmin=0, vmax=1, colorbar=True
        )

    result = ab.draw_propertylayer(
        space, space._mesa_property_layers, propertylayer_portrayal_colormap
    )
    assert result is not None

    # Test with no color or colormap
    def propertylayer_portrayal(layer):
        return PropertyLayerStyle(
            color=None, colormap=None, alpha=1.0, vmin=0, vmax=1, colorbar=False
        )

    with pytest.raises(ValueError, match="Specify one of 'color' or 'colormap'"):
        ab.draw_propertylayer(
            space, space._mesa_property_layers, propertylayer_portrayal
        )


def test_backend_get_agent_pos():
    """Test extracting agent position from pos and cell.coordinate attributes."""
    mb = MatplotlibBackend(space_drawer=MagicMock())

    class AgentWithPos:
        pos = (1, 2)

    x, y = mb._get_agent_pos(AgentWithPos(), None)
    assert (x, y) == (1, 2)

    class AgentWithCell:
        pos = None
        cell = types.SimpleNamespace(coordinate=(3, 4))

    x, y = mb._get_agent_pos(AgentWithCell(), None)
    assert (x, y) == (3, 4)


def test_backends_handle_errors():
    """Test error handling scenarios for invalid agent/propertylayer data."""
    mb = MatplotlibBackend(space_drawer=MagicMock())
    mb.initialize_canvas()
    arguments = {
        "loc": np.array([[0, 0]]),
        "marker": np.array(["o"]),
        "zorder": np.array([1]),
        "s": np.array([5]),
        "c": np.array(["red"]),
        "alpha": np.array([1.0]),
        "edgecolors": np.array(["black"]),
        "linewidths": np.array([1]),
    }
    with pytest.raises(ValueError):
        mb.draw_agents(arguments, edgecolors="blue")


def test_altair_backend_draw_agents_with_icons():
    """Test draw_agents renders icons when icon_rasters are provided."""
    ab = AltairBackend(space_drawer=MagicMock())
    ab.space_drawer.get_viz_limits = MagicMock(return_value=(0, 10, 0, 10))

    # Create a fake data URL for testing
    fake_icon_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    arguments = {
        "loc": np.array([[1, 1], [2, 2], [3, 3]]),
        "size": np.array([10, 10, 10]),
        "shape": np.array(["circle", "circle", "circle"]),
        "opacity": np.array([1.0, 1.0, 1.0]),
        "strokeWidth": np.array([1, 1, 1]),
        "color": np.array(["red", "blue", "green"]),
        "filled": np.array([True, True, True]),
        "stroke": np.array(["black", "black", "black"]),
        # Icon rasters - some with icons, some without (None)
        "icon_rasters": np.array([fake_icon_url, None, fake_icon_url], dtype=object),
    }

    result = ab.draw_agents(arguments)

    # Should return a layered chart (icons + markers)
    assert result is not None
    # The result should be an Altair chart
    assert isinstance(result, (alt.Chart, alt.LayerChart))


def test_altair_backend_draw_agents_without_icons():
    """Test draw_agents uses markers when no icon_rasters provided."""
    ab = AltairBackend(space_drawer=MagicMock())
    ab.space_drawer.get_viz_limits = MagicMock(return_value=(0, 10, 0, 10))

    arguments = {
        "loc": np.array([[1, 1], [2, 2]]),
        "size": np.array([10, 10]),
        "shape": np.array(["circle", "square"]),
        "opacity": np.array([1.0, 1.0]),
        "strokeWidth": np.array([1, 1]),
        "color": np.array(["red", "blue"]),
        "filled": np.array([True, True]),
        "stroke": np.array(["black", "black"]),
        # No icon_rasters key at all
    }

    result = ab.draw_agents(arguments)

    assert result is not None
    assert isinstance(result, (alt.Chart, alt.LayerChart))


def test_altair_backend_draw_agents_with_all_none_icons():
    """Test draw_agents handles case where all icon_rasters are None."""
    ab = AltairBackend(space_drawer=MagicMock())
    ab.space_drawer.get_viz_limits = MagicMock(return_value=(0, 10, 0, 10))

    arguments = {
        "loc": np.array([[1, 1], [2, 2]]),
        "size": np.array([10, 10]),
        "shape": np.array(["circle", "circle"]),
        "opacity": np.array([1.0, 1.0]),
        "strokeWidth": np.array([1, 1]),
        "color": np.array(["red", "blue"]),
        "filled": np.array([True, True]),
        "stroke": np.array(["black", "black"]),
        # All icons are None - should fall back to markers
        "icon_rasters": np.array([None, None], dtype=object),
    }

    result = ab.draw_agents(arguments)

    assert result is not None
    assert isinstance(result, (alt.Chart, alt.LayerChart))


def test_altair_backend_draw_agents_with_culling():
    """Test draw_agents with culling enabled filters out-of-bounds agents."""
    ab = AltairBackend(space_drawer=MagicMock())
    # Set viewport to only show x=0-5, y=0-5
    ab.space_drawer.get_viz_limits = MagicMock(return_value=(0, 5, 0, 5))

    arguments = {
        "loc": np.array([[1, 1], [10, 10], [2, 2]]),  # Agent at (10,10) is outside
        "size": np.array([10, 10, 10]),
        "shape": np.array(["circle", "circle", "circle"]),
        "opacity": np.array([1.0, 1.0, 1.0]),
        "strokeWidth": np.array([1, 1, 1]),
        "color": np.array(["red", "blue", "green"]),
        "filled": np.array([True, True, True]),
        "stroke": np.array(["black", "black", "black"]),
    }

    result = ab.draw_agents(arguments, enable_culling=True)

    assert result is not None
    assert isinstance(result, (alt.Chart, alt.LayerChart))


def test_altair_backend_collect_agent_data_preserves_portrayals():
    """Test collect_agent_data preserves original portrayal objects for icon enrichment."""
    ab = AltairBackend(space_drawer=MagicMock())

    class DummyAgent:
        pos = (0, 0)

    class DummySpace:
        agents = [DummyAgent()]

    def agent_portrayal_with_icon(agent):
        return {
            "size": 24,
            "color": "red",
            "marker": "o",
            "icon": "smiley",
            "icon_size": 32,
        }

    data = ab.collect_agent_data(DummySpace(), agent_portrayal_with_icon)

    # Check that portrayals are preserved
    assert "portrayals" in data
    assert len(data["portrayals"]) == 1
    assert data["portrayals"][0]["icon"] == "smiley"
    assert data["portrayals"][0]["icon_size"] == 32
