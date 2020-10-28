from unittest import TestCase
from collections import defaultdict

from mesa.model import Model
from mesa.space import Grid
from mesa.time import SimultaneousActivation
from mesa.visualization.ModularVisualization import (
    ModularServer,
    render_model,
    reset_model,
    user_params,
)
from mesa.visualization.modules import CanvasGrid, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from tests.test_batchrunner import MockAgent


class MockModel(Model):
    """ Test model for testing """

    def __init__(self, width, height, key1=103, key2=104):

        self.width = width
        self.height = height
        self.key1 = (key1,)
        self.key2 = key2
        self.schedule = SimultaneousActivation(self)
        self.grid = Grid(width, height, torus=True)

        for (c, x, y) in self.grid.coord_iter():
            a = MockAgent(x + y * 100, self, x * y * 3)
            self.grid.place_agent(a, (x, y))
            self.schedule.add(a)

    def step(self):
        self.schedule.step()


class TestModularServer(TestCase):
    """ Test server for testing """

    def portrayal(self, cell):
        return {
            "Shape": "rect",
            "w": 1,
            "h": 1,
            "Filled": "true",
            "Layer": 0,
            "x": 0,
            "y": 0,
            "Color": "black",
        }

    def setUp(self):

        self.user_params = {
            "width": 1,
            "height": 1,
            "key1": UserSettableParameter("number", "Test Parameter", 101),
            "key2": UserSettableParameter("slider", "Test Parameter", 200, 0, 300, 10),
        }

        self.viz_elements = [
            CanvasGrid(self.portrayal, 10, 10, 20, 20),
            TextElement(),
            # ChartModule([{"Label": "Wolves", "Color": "#AA0000"},  # Todo - test chart module
            #              {"Label": "Sheep", "Color": "#666666"}])
        ]

        self.server = ModularServer(
            MockModel, self.viz_elements, "Test Model", model_params=self.user_params
        )

        self.model = MockModel(width=1, height=1, key1=101, key2=200)

    def test_reset_model(self):
        server_model = reset_model(self.server.model_cls, self.server.model_kwargs)
        assert self.model.key1 == server_model.key1
        assert self.model.key2 == server_model.key2

    def test_canvas_render_model_state(self):

        test_portrayal = self.portrayal(None)
        test_grid_state = defaultdict(list)
        test_grid_state[test_portrayal["Layer"]].append(test_portrayal)

        state = render_model(self.model, self.server.visualization_elements)
        assert state[0] == test_grid_state

    def test_text_render_model_state(self):
        state = render_model(self.model, self.server.visualization_elements)
        assert state[1] == "<b>VisualizationElement goes here</b>."

    def test_user_params(self):
        assert user_params(self.server.model_kwargs) == {
            "key1": UserSettableParameter("number", "Test Parameter", 101).json,
            "key2": UserSettableParameter(
                "slider", "Test Parameter", 200, 0, 300, 10
            ).json,
        }
