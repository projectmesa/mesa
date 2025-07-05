"""Test cases for the SpaceRenderer class in Mesa."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

import mesa
from mesa.discrete_space import (
    HexGrid,
    Network,
    OrthogonalMooreGrid,
    PropertyLayer,
    VoronoiGrid,
)
from mesa.space import (
    ContinuousSpace,
    HexMultiGrid,
    HexSingleGrid,
    MultiGrid,
    NetworkGrid,
    SingleGrid,
)
from mesa.visualization.backends import altair_backend, matplotlib_backend
from mesa.visualization.components import PropertyLayerStyle
from mesa.visualization.space_drawers import (
    ContinuousSpaceDrawer,
    HexSpaceDrawer,
    NetworkSpaceDrawer,
    OrthogonalSpaceDrawer,
    VoronoiSpaceDrawer,
)
from mesa.visualization.space_renderer import SpaceRenderer


class CustomModel(mesa.Model):
    """A simple model for testing purposes."""

    def __init__(self, seed=None):  # noqa: D107
        super().__init__(seed=seed)
        self.grid = mesa.discrete_space.OrthogonalMooreGrid([2, 2])
        self.layer = PropertyLayer("test", [2, 2], default_value=0)

        self.grid.add_property_layer(self.layer)


def test_backend_selection():
    """Test that the SpaceRenderer selects the correct backend."""
    model = CustomModel()
    sr = SpaceRenderer(model, backend="matplotlib")
    assert isinstance(sr.backend_renderer, matplotlib_backend.MatplotlibBackend)
    sr = SpaceRenderer(model, backend="altair")
    assert isinstance(sr.backend_renderer, altair_backend.AltairBackend)
    with pytest.raises(ValueError):
        SpaceRenderer(model, backend=None)


@pytest.mark.parametrize(
    "grid,expected_drawer",
    [
        (OrthogonalMooreGrid([2, 2]), OrthogonalSpaceDrawer),
        (SingleGrid(width=2, height=2, torus=False), OrthogonalSpaceDrawer),
        (MultiGrid(width=2, height=2, torus=False), OrthogonalSpaceDrawer),
        (HexGrid([2, 2]), HexSpaceDrawer),
        (HexSingleGrid(width=2, height=2, torus=False), HexSpaceDrawer),
        (HexMultiGrid(width=2, height=2, torus=False), HexSpaceDrawer),
        (Network(G=MagicMock()), NetworkSpaceDrawer),
        (NetworkGrid(g=MagicMock()), NetworkSpaceDrawer),
        (ContinuousSpace(x_max=2, y_max=2, torus=False), ContinuousSpaceDrawer),
        (VoronoiGrid([[0, 0], [1, 1]]), VoronoiSpaceDrawer),
    ],
)
def test_space_drawer_selection(grid, expected_drawer):
    """Test that the SpaceRenderer selects the correct space drawer based on the grid type."""
    model = CustomModel()
    with patch.object(model, "grid", new=grid):
        sr = SpaceRenderer(model)
        assert isinstance(sr.space_drawer, expected_drawer)


def test_map_coordinates():
    """Test that the SpaceRenderer maps the coordinates correctly based on the grid type."""
    model = CustomModel()

    sr = SpaceRenderer(model)
    arr = np.array([[1, 2], [3, 4]])
    args = {"loc": arr}
    mapped = sr._map_coordinates(args)

    # same for orthogonal grids
    assert np.array_equal(mapped["loc"], arr)

    with patch.object(model, "grid", new=HexGrid([2, 2])):
        sr = SpaceRenderer(model)
        mapped = sr._map_coordinates(args)

        assert not np.array_equal(mapped["loc"], arr)
        assert mapped["loc"].shape == arr.shape

    with patch.object(model, "grid", new=Network(G=MagicMock())):
        sr = SpaceRenderer(model)
        # Patch the space_drawer.pos to provide a mapping for the test
        sr.space_drawer.pos = {0: (0, 0), 1: (1, 1), 2: (2, 2), 3: (3, 3)}
        mapped = sr._map_coordinates(args)

        assert not np.array_equal(mapped["loc"], arr)
        assert mapped["loc"].shape == arr.shape


def test_render_calls():
    """Test that the render method calls the appropriate drawing methods."""
    model = CustomModel()
    sr = SpaceRenderer(model)

    sr.draw_structure = MagicMock()
    sr.draw_agents = MagicMock()
    sr.draw_propertylayer = MagicMock()

    sr.render(
        agent_portrayal=lambda _: {},
        propertylayer_portrayal=lambda _: PropertyLayerStyle(color="red"),
    )

    sr.draw_structure.assert_called_once()
    sr.draw_agents.assert_called_once()
    sr.draw_propertylayer.assert_called_once()


def test_no_property_layers():
    """Test to confirm the SpaceRenderer raises an exception when no property layers are found."""
    model = CustomModel()
    sr = SpaceRenderer(model)

    # Simulate missing property layer in the grid
    with (
        patch.object(model.grid, "_mesa_property_layers", new={}),
        pytest.raises(Exception, match="No property layers were found on the space."),
    ):
        sr.draw_propertylayer(lambda _: PropertyLayerStyle(color="red"))
