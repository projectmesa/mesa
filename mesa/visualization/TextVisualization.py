'''
Text Visualization
=======================

Base class for an ASCII-only visualization of a model.
'''

class TextVisualization(object):
    '''
    ASCII-Only visualization of a model.

    Properties:

        model: The underlying model object to be visualized.
        elements: List of visualization elements, which will be rendered 
                    in the order they are adedd.

    '''

    model = None
    elements = []

    def __init__(self, model):
        '''
        Create a new Text Visualization object.
        '''
        self.model = model
        self.elements = []

    def render(self):
        '''
        Render all the text elements, in order.
        '''
        for element in self.elements:
            print element

    def step(self):
        '''
        Advance the model by a step and print the results.
        '''
        self.model.step()
        self.render()
        
    def step_forward(self, steps):
        '''
        Advance the model by some # of steps and show the result.
        '''
        for i in range(steps):
            self.model.step()
        self.render()




class TextElement(object):
    '''
    Base class for all TextElements to render.

    Methods:
        render: 'Renders' some data into ASCII and returns.
        __str__: Displays render() by default.
    '''

    def __init__(self):
        pass

    def render(self):
        return "Placeholder!"

    def __str__(self):
        return self.render()

class TextData(TextElement):
    '''
    Prints the value of one particular variable from the base model.
    '''
    def __init__(self, model, var_name):
        '''
        Create a new data renderer.
        '''
        self.model = model
        self.var_name = var_name

    def render(self):
        return self.var_name + ": " + str(getattr(self.model, self.var_name))


class TextGrid(TextElement):
    '''
    Class for creating an ASCII visualization of a basic grid object.

    By default, assume that each cell is represented by one character, and
    that empty cells are rendered as ' ' characters. When printed, the TextGrid
    results in a width x height grid of ascii characters.

    Properties:
        grid: The underlying grid object.
        converter: Function which renders the contents of each cell. 
    '''

    grid = None
    converter = lambda x: 'X'

    def __init__(self, grid, converter):
        '''
        Create a new ASCII grid visualization.

        Args:
            grid: The underlying Grid object.
            converter: function for converting the content of each cell to ascii
        '''
        self.grid = grid
        self.converter = converter

    def render(self):
        '''
        What to show when printed.
        '''
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





