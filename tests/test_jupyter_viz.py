import unittest
from unittest.mock import Mock, patch

import solara

from mesa.experimental.jupyter_viz import JupyterViz, make_user_input


class TestMakeUserInput(unittest.TestCase):
    def test_unsupported_type(self):
        """unsupported input type should raise ValueError"""
        # bogus type
        with self.assertRaisesRegex(ValueError, "not a supported input type"):
            make_user_input(10, "input", {"type": "bogus"})
        # no type is specified
        with self.assertRaisesRegex(ValueError, "not a supported input type"):
            make_user_input(10, "input", {})

    @patch("mesa.experimental.jupyter_viz.solara")
    def test_slider_int(self, mock_solara):
        value = 10
        name = "num_agents"
        options = {
            "type": "SliderInt",
            "label": "number of agents",
            "min": 10,
            "max": 20,
            "step": 1,
        }
        make_user_input(value, name, options)
        mock_solara.SliderInt.assert_called_with(
            options["label"],
            value=value,
            min=options["min"],
            max=options["max"],
            step=options["step"],
        )

    @patch("mesa.experimental.jupyter_viz.solara")
    def test_label_fallback(self, mock_solara):
        """name should be used as fallback label"""
        value = 10
        name = "num_agents"
        options = {
            "type": "SliderInt",
        }
        make_user_input(value, name, options)
        mock_solara.SliderInt.assert_called_with(
            name, value=value, min=None, max=None, step=None
        )


class TestJupyterViz(unittest.TestCase):
    @patch("mesa.experimental.jupyter_viz.make_space")
    def test_call_space_drawer(self, mock_make_space):
        mock_model_class = Mock()
        agent_portrayal = {
            "Shape": "circle",
            "color": "gray",
        }
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
        mock_make_space.assert_called_with(
            mock_model_class.return_value, agent_portrayal
        )

        # specify no space should be drawn; any false value should work
        for falsy_value in [None, False, 0]:
            mock_make_space.reset_mock()
            solara.render(
                JupyterViz(
                    model_class=mock_model_class,
                    model_params={},
                    agent_portrayal=agent_portrayal,
                    space_drawer=falsy_value,
                )
            )
            # should call default method with class instance and agent portrayal
            assert mock_make_space.call_count == 0

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
