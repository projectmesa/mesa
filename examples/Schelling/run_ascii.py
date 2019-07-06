from mesa.visualization.TextVisualization import (
    TextData, TextGrid, TextVisualization
)

from model import Schelling


class SchellingTextVisualization(TextVisualization):
    '''
    ASCII visualization for schelling model
    '''

    def __init__(self, model):
        '''
        Create new Schelling ASCII visualization.
        '''
        self.model = model

        grid_viz = TextGrid(self.model.grid, self.print_ascii_agent)
        happy_viz = TextData(self.model, 'happy')
        self.elements = [grid_viz, happy_viz]

    @staticmethod
    def print_ascii_agent(a):
        '''
        Minority agents are X, Majority are O.
        '''
        if a.type == 0:
            return 'O'
        if a.type == 1:
            return 'X'


if __name__ == '__main__':
    model_params = {
        "height": 20,
        "width": 20,
        # Agent density, from 0.8 to 1.0
        "density": 0.8,
        # Fraction minority, from 0.2 to 1.0
        "minority_pc": 0.2,
        # Homophily, from 3 to 8
        "homophily": 3
    }

    model = Schelling(**model_params)
    viz = SchellingTextVisualization(model)
    for i in range(10):
        print("Step:", i)
        viz.step()
        print('---')
