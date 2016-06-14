# -*- coding: utf-8 -*-
"""
Text Visualization
==================

Base classes for ASCII-only visualizations of a model.
These are useful for quick debugging, and can readily be rendered in an IPython
Notebook or via text alone in a browser window.

Classes:

TextVisualization: Class meant to wrap around a Model object and render it
in some way using Elements, which are stored in a list and rendered in that
order. Each element, in turn, renders a particular piece of information as
text.

TextElement: Parent class for all other ASCII elements. render() returns its
representative string, which can be printed via the overloaded __str__ method.

TextData: Uses getattr to get the value of a particular property of a model
and prints it, along with its name.

TextGrid: Prints a grid, assuming that the value of each cell maps to exactly
one ASCII character via a converter method. This (as opposed to a dictionary)
is used so as to allow the method to access Agent internals, as well as to
potentially render a cell based on several values (e.g. an Agent grid and a
Patch value grid).

"""
# Pylint instructions: allow single-character variable names.
# pylint: disable=invalid-name


class TextVisualization:
    """ ASCII-Only visualization of a model.

    Properties:

        model: The underlying model object to be visualized.
        elements: List of visualization elements, which will be rendered
                    in the order they are added.

    """
    def __init__(self, model):
        """ Create a new Text Visualization object. """
        self.model = model
        self.elements = []

    def render(self):
        """ Render all the text elements, in order. """
        for element in self.elements:
            print(element)

    def step(self):
        """ Advance the model by a step and print the results. """
        self.model.step()
        self.render()


class TextElement:
    """ Base class for all TextElements to render.

    Methods:
        render: 'Renders' some data into ASCII and returns.
        __str__: Displays render() by default.
    """

    def __init__(self):
        pass

    def render(self):
        """ Render the element as text. """
        return "Placeholder!"

    def __str__(self):
        return self.render()


class TextData(TextElement):
    """ Prints the value of one particular variable from the base model. """
    def __init__(self, model, var_name):
        """ Create a new data renderer. """
        self.model = model
        self.var_name = var_name

    def render(self):
        return self.var_name + ": " + str(getattr(self.model, self.var_name))


class TextGrid(TextElement):
    """ Class for creating an ASCII visualization of a basic grid object.

    By default, assume that each cell is represented by one character, and
    that empty cells are rendered as ' ' characters. When printed, the TextGrid
    results in a width x height grid of ascii characters.

    Properties:
        grid: The underlying grid object.

    """
    grid = None

    def __init__(self, grid, converter):
        """ Create a new ASCII grid visualization.

        Args:
            grid: The underlying Grid object.
            converter: function for converting the content of each cell
            to ascii
        """
        self.grid = grid

    @staticmethod
    def converter(x):
        """ Text content of cells. """
        return 'X'

    def render(self):
        """ What to show when printed. """
        viz = ""
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                c = self.grid[y][x]
                if c is None:
                    viz += ' '
                else:
                    viz += self.converter(c)
            viz += '\n'
        return viz
