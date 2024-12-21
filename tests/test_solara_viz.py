"""Test Solara visualizations."""

import unittest

import ipyvuetify as vw
import pytest
import solara

import mesa
import mesa.visualization.components.altair_components
import mesa.visualization.components.matplotlib_components
from mesa.visualization.components.matplotlib_components import make_mpl_space_component
from mesa.visualization.solara_viz import (
    Slider,
    SolaraViz,
    UserInputs,
    _check_model_params,
)


class TestMakeUserInput(unittest.TestCase):  # noqa: D101
    def test_unsupported_type(self):  # noqa: D102
        @solara.component
        def Test(user_params):
            UserInputs(user_params)

        """unsupported input type should raise ValueError"""
        # bogus type
        with self.assertRaisesRegex(ValueError, "not a supported input type"):
            solara.render(Test({"mock": {"type": "bogus"}}), handle_error=False)

        # no type is specified
        with self.assertRaisesRegex(ValueError, "not a supported input type"):
            solara.render(Test({"mock": {}}), handle_error=False)

    def test_slider_int(self):  # noqa: D102
        @solara.component
        def Test(user_params):
            UserInputs(user_params)

        options = {
            "type": "SliderInt",
            "value": 10,
            "label": "number of agents",
            "min": 10,
            "max": 20,
            "step": 1,
        }
        user_params = {"num_agents": options}
        _, rc = solara.render(Test(user_params), handle_error=False)
        slider_int = rc.find(vw.Slider).widget

        assert slider_int.v_model == options["value"]
        assert slider_int.label == options["label"]
        assert slider_int.min == options["min"]
        assert slider_int.max == options["max"]
        assert slider_int.step == options["step"]

    def test_checkbox(self):  # noqa: D102
        @solara.component
        def Test(user_params):
            UserInputs(user_params)

        options = {"type": "Checkbox", "value": True, "label": "On"}
        user_params = {"num_agents": options}
        _, rc = solara.render(Test(user_params), handle_error=False)
        checkbox = rc.find(vw.Checkbox).widget

        assert checkbox.v_model == options["value"]
        assert checkbox.label == options["label"]

    def test_label_fallback(self):
        """Name should be used as fallback label."""

        @solara.component
        def Test(user_params):
            UserInputs(user_params)

        options = {
            "type": "SliderInt",
            "value": 10,
        }

        user_params = {"num_agents": options}
        _, rc = solara.render(Test(user_params), handle_error=False)
        slider_int = rc.find(vw.Slider).widget

        assert slider_int.v_model == options["value"]
        assert slider_int.label == "num_agents"
        assert slider_int.min is None
        assert slider_int.max is None
        assert slider_int.step is None


def test_call_space_drawer(mocker):  # noqa: D103
    mock_space_matplotlib = mocker.spy(
        mesa.visualization.components.matplotlib_components, "SpaceMatplotlib"
    )

    mock_space_altair = mocker.spy(
        mesa.visualization.components.altair_components, "SpaceAltair"
    )

    class MockModel(mesa.Model):
        def __init__(self, seed=None):
            super().__init__(seed=seed)

    model = MockModel()
    mocker.patch.object(mesa.Model, "__init__", return_value=None)

    agent_portrayal = {
        "marker": "circle",
        "color": "gray",
    }
    propertylayer_portrayal = None
    # initialize with space drawer unspecified (use default)
    # component must be rendered for code to run
    solara.render(
        SolaraViz(
            model,
            components=[make_mpl_space_component(agent_portrayal)],
        )
    )
    # should call default method with class instance and agent portrayal
    mock_space_matplotlib.assert_called_with(
        model, agent_portrayal, propertylayer_portrayal, post_process=None
    )

    # specify no space should be drawn
    mock_space_matplotlib.reset_mock()
    solara.render(SolaraViz(model))
    # should call default method with class instance and agent portrayal
    assert mock_space_matplotlib.call_count == 0
    assert mock_space_altair.call_count == 0

    # specify a custom space method
    class AltSpace:
        @staticmethod
        def drawer(model):
            return

    altspace_drawer = mocker.spy(AltSpace, "drawer")
    solara.render(SolaraViz(model, components=[AltSpace.drawer]))
    altspace_drawer.assert_called_with(model)

    # check voronoi space drawer
    voronoi_model = mesa.Model()
    voronoi_model.grid = mesa.experimental.cell_space.VoronoiGrid(
        centroids_coordinates=[(0, 1), (0, 0), (1, 0)],
    )
    solara.render(
        SolaraViz(voronoi_model, components=[make_mpl_space_component(agent_portrayal)])
    )


def test_slider():  # noqa: D103
    slider_float = Slider("Agent density", 0.8, 0.1, 1.0, 0.1)
    assert slider_float.is_float_slider
    assert slider_float.value == 0.8
    assert slider_float.get("value") == 0.8
    assert slider_float.min == 0.1
    assert slider_float.max == 1.0
    assert slider_float.step == 0.1
    slider_int = Slider("Homophily", 3, 0, 8, 1)
    assert not slider_int.is_float_slider
    slider_dtype_float = Slider("Homophily", 3, 0, 8, 1, dtype=float)
    assert slider_dtype_float.is_float_slider


def test_model_param_checks():  # noqa: D103
    class ModelWithOptionalParams:
        def __init__(self, required_param, optional_param=10):
            pass

    class ModelWithOnlyRequired:
        def __init__(self, param1, param2):
            pass

    class ModelWithKwargs:
        def __init__(self, **kwargs):
            pass

    # Test that optional params can be omitted
    _check_model_params(ModelWithOptionalParams.__init__, {"required_param": 1})

    # Test that optional params can be provided
    _check_model_params(
        ModelWithOptionalParams.__init__, {"required_param": 1, "optional_param": 5}
    )

    # Test that model_params are accepted if model uses **kwargs
    _check_model_params(ModelWithKwargs.__init__, {"another_kwarg": 6})

    # test hat kwargs are accepted even if no model_params are specified
    _check_model_params(ModelWithKwargs.__init__, {})

    # Test invalid parameter name raises ValueError
    with pytest.raises(ValueError, match="Invalid model parameter: invalid_param"):
        _check_model_params(
            ModelWithOptionalParams.__init__, {"required_param": 1, "invalid_param": 2}
        )

    # Test missing required parameter raises ValueError
    with pytest.raises(ValueError, match="Missing required model parameter: param2"):
        _check_model_params(ModelWithOnlyRequired.__init__, {"param1": 1})

    # Test passing extra parameters raises ValueError
    with pytest.raises(ValueError, match="Invalid model parameter: extra"):
        _check_model_params(
            ModelWithOnlyRequired.__init__, {"param1": 1, "param2": 2, "extra": 3}
        )

    # Test empty params dict raises ValueError if required params
    with pytest.raises(ValueError, match="Missing required model parameter"):
        _check_model_params(ModelWithOnlyRequired.__init__, {})


# test that _check_model_params raises ValueError when *args are present
def test_check_model_params_with_args_only():
    """Test that _check_model_params raises ValueError when *args are present."""

    class ModelWithArgsOnly:
        def __init__(self, param1, *args):
            pass

    model_params = {"param1": 1}

    with pytest.raises(
        ValueError,
        match="Mesa's visualization requires the use of keyword arguments to ensure the parameters are passed to Solara correctly. Please ensure all model parameters are of form param=value",
    ):
        _check_model_params(ModelWithArgsOnly.__init__, model_params)
