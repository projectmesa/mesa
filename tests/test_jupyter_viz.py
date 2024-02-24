import unittest
from unittest.mock import Mock, patch

import ipyvuetify as vw
import solara

from mesa.experimental.jupyter_viz import JupyterViz, Slider, UserInputs


class TestMakeUserInput(unittest.TestCase):
    def test_unsupported_type(self):
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

    def test_slider_int(self):
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

    def test_checkbox(self):
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
        """name should be used as fallback label"""

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


class TestJupyterViz(unittest.TestCase):
    @patch("mesa.experimental.components.matplotlib.SpaceMatplotlib")
    def test_call_space_drawer(self, mock_space_matplotlib):
        mock_model_class = Mock()
        mock_model_class.__name__ = "MockModelClass"
        agent_portrayal = {
            "Shape": "circle",
            "color": "gray",
        }
        current_step = 0
        dependencies = [current_step]
        # initialize with space drawer unspecified (use default)
        # component must be rendered for code to run
        solara.render(
            JupyterViz(
                model_class=mock_model_class,
                model_params={},
                agent_portrayal=agent_portrayal,
            )
        )
        # should call default method with class instance and agent portrayal
        mock_space_matplotlib.assert_called_with(
            mock_model_class.return_value, agent_portrayal, dependencies=dependencies
        )

        # specify no space should be drawn; any false value should work
        for falsy_value in [None, False, 0]:
            mock_space_matplotlib.reset_mock()
            solara.render(
                JupyterViz(
                    model_class=mock_model_class,
                    model_params={},
                    agent_portrayal=agent_portrayal,
                    space_drawer=falsy_value,
                )
            )
            # should call default method with class instance and agent portrayal
            assert mock_space_matplotlib.call_count == 0

        # specify a custom space method
        altspace_drawer = Mock()
        solara.render(
            JupyterViz(
                model_class=mock_model_class,
                model_params={},
                agent_portrayal=agent_portrayal,
                space_drawer=altspace_drawer,
            )
        )
        altspace_drawer.assert_called_with(
            mock_model_class.return_value, agent_portrayal
        )


def test_slider():
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
