'''
Modular text rendering.

'''

from mesa.visualization.ModularVisualization import VisualizationElement


class TextElement(VisualizationElement):
    js_includes = ["TextModule.js"]
    js_code = "elements.push(new TextModule());"
