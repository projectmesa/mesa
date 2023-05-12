from unittest import TestCase

from mesa.visualization.UserParam import (
    Checkbox,
    Choice,
    NumberInput,
    Slider,
    StaticText,
)


class TestOption(TestCase):
    def setUp(self):
        self.number_option = NumberInput("number", value=123)
        self.checkbox_option = Checkbox(value=True)
        self.choice_option = Choice(
            value="I am your default choice",
            choices=["I am your default choice", "I am your other choice"],
        )
        self.slider_option = Slider(value=123, min_value=100, max_value=200)
        self.static_text_option = StaticText("Hurr, Durr Im'a Sheep")

    def test_number(self):
        option = self.number_option
        assert option.value == 123
        option.value = 321
        assert option.value == 321

    def test_checkbox(self):
        option = self.checkbox_option
        assert option.value
        option.value = False
        assert not option.value

    def test_choice(self):
        option = self.choice_option
        assert option.value == "I am your default choice"
        option.value = "I am your other choice"
        assert option.value == "I am your other choice"
        option.value = "I am not an available choice"
        assert option.value == "I am your default choice"

    def test_slider(self):
        option = self.slider_option
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
