from unittest import TestCase
from collections import defaultdict

from mesa.model import Model
from mesa.space import Grid
from mesa.time import SimultaneousActivation
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, TextElement

from test_batchrunner import MockAgent


class MockModel(Model):
    """ Test model for testing """

    def __init__(self, width, height, key1=103, key2=104):

        self.width = width
        self.height = height
        self.key1 = key1,
        self.key2 = key2
        self.schedule = SimultaneousActivation(self)
        self.grid = Grid(width, height, torus=True)

        for (c, x, y) in self.grid.coord_iter():
            a = MockAgent(x + y * 100, x * y * 3)
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
            "Color": "black"
        }

    def setUp(self):

        self.keyword_params = {
            'key1': 201,
            'key2': 202
        }

        self.viz_elements = [
            CanvasGrid(self.portrayal, 10, 10, 20, 20),
            TextElement(),
            # ChartModule([{"Label": "Wolves", "Color": "#AA0000"},  # Todo - test chart module
            #              {"Label": "Sheep", "Color": "#666666"}])
        ]

        self.server = ModularServer(MockModel, self.viz_elements, "Test Model", 1, 1, **self.keyword_params,
                                    exclude_list=['key2', 'height', 'width'])

    def test_user_params(self):
        assert self.server.user_params != {'key1': 201, 'key2': 202}    # ensure exclude list takes affect
        assert self.server.user_params == {'key1': 201}

    def test_canvas_render_model_state(self):

        test_portrayal = self.portrayal(None)
        test_grid_state = defaultdict(list)
        test_grid_state[test_portrayal['Layer']].append(test_portrayal)

        state = self.server.render_model()
        assert state[0] == test_grid_state

    def test_text_render_model_state(self):
        state = self.server.render_model()
        assert state[1] == '<b>VisualizationElement goes here</b>.'

    def test_reset_model(self):
        self.server.model_kwargs['key1'] = 301
        self.server.reset_model()
        assert self.server.user_params == {'key1': 301}

    def test_exclude_list(self):
        assert self.server.exclude_list == ['key2', 'height', 'width']
