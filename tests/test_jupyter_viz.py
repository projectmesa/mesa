import unittest
from unittest.mock import patch

from mesa.experimental.jupyter_viz import make_user_input


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
