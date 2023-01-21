from unittest import TestCase

from mesa.visualization.UserParam import (
    Checkbox,
    Choice,
    NumberInput,
    Slider,
    StaticText,
    UserSettableParameter,
)


class TestOption(TestCase):
    def setUp(self):
        self.number_option = UserSettableParameter("number", value=123)
        self.number_option_standalone = NumberInput("number", value=123)
        self.checkbox_option = UserSettableParameter("checkbox", value=True)
        self.checkbox_option_standalone = Checkbox(value=True)
        self.choice_option = UserSettableParameter(
            "choice",
            value="I am your default choice",
            choices=["I am your default choice", "I am your other choice"],
        )
        self.choice_option_standalone = Choice(
            value="I am your default choice",
            choices=["I am your default choice", "I am your other choice"],
        )
        self.slider_option = UserSettableParameter(
            "slider", value=123, min_value=100, max_value=200
        )
        self.slider_option_standalone = Slider(value=123, min_value=100, max_value=200)
        self.static_text_option = StaticText("Hurr, Durr Im'a Sheep")

    def test_number(self):
        for option in [self.number_option, self.number_option_standalone]:
            assert option.value == 123
            option.value = 321
            assert option.value == 321

    def test_checkbox(self):
        for option in [self.checkbox_option, self.checkbox_option_standalone]:
            assert option.value
            option.value = False
            assert not option.value

    def test_choice(self):
        for option in [self.choice_option, self.choice_option_standalone]:
            assert option.value == "I am your default choice"
            option.value = "I am your other choice"
            assert option.value == "I am your other choice"
            option.value = "I am not an available choice"
            assert option.value == "I am your default choice"

    def test_slider(self):
        for option in [self.slider_option, self.slider_option_standalone]:
            assert option.value == 123
            option.value = 150
            assert option.value == 150
            option.value = 0
            assert option.value == 100
            option.value = 300
            assert option.value == 200
            assert option.json["value"] == 200
        with self.assertRaises(ValueError):
            Slider()

    def test_static_text(self):
        assert self.static_text_option.value == "Hurr, Durr Im'a Sheep"
