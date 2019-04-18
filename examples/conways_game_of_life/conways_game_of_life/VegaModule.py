import json

from mesa.visualization.ModularVisualization import VisualizationElement


class VegaGrid(VisualizationElement):
    local_includes = ["conways_game_of_life/" + js for js in ["vega.js", "vega-lite.js", "vegaEmbed.js", "vegaModule.js"]]

    def __init__(self):
        '''
        Instantiate a new vegaModule
        '''
        self.js_code = "elements.push(new vegaGrid());"

    def render(self, model):
        space_state = []
        for agent in model.schedule.agents:
            portrayal = {"x": agent.x, "y": agent.y, "alive": agent.isAlive}
            space_state.append(portrayal)
        return json.dumps(space_state)
