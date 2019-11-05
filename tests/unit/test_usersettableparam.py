from unittest import TestCase
from mesa.visualization.UserParam import UserSettableParameter


class TestOption(TestCase):

    def setUp(self):
        self.number_option = UserSettableParameter('number', value=123)
        self.checkbox_option = UserSettableParameter('checkbox', value=True)
        self.choice_option = UserSettableParameter('choice', value='I am your default choice', choices=['I am your default choice',
                                                                                         'I am your other choice'])
        self.slider_option = UserSettableParameter('slider', value=123, min_value=100, max_value=200)

    def test_number(self):
        assert self.number_option.value == 123
        self.number_option.value = 321
        assert self.number_option.value == 321

    def test_checkbox(self):
        assert self.checkbox_option.value
        self.checkbox_option.value = False
        assert not self.checkbox_option.value

    def test_choice(self):
        assert self.choice_option.value == 'I am your default choice'
        self.choice_option.value = 'I am your other choice'
        assert self.choice_option.value == 'I am your other choice'
        self.choice_option.value = 'I am not an available choice'
        assert self.choice_option.value == 'I am your default choice'

    def test_slider(self):
        assert self.slider_option.value == 123
        self.slider_option.value = 150
        assert self.slider_option.value == 150
        self.slider_option.value = 0
        assert self.slider_option.value == 100
        self.slider_option.value = 300
        assert self.slider_option.value == 200
