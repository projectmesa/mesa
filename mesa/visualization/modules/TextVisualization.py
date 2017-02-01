# -*- coding: utf-8 -*-
"""
Text Module
============

Module for drawing live-updating text.

"""
from mesa.visualization.ModularVisualization import VisualizationElement


class TextElement(VisualizationElement):
    package_includes = ["TextModule.js"]
    js_code = "elements.push(new TextModule());"
