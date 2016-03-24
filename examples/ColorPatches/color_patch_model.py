"""
The model - a 2D lattice where agents live and have an opinion
"""


import random

from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import Grid
from color_cell import ColorCell



class ColorPatchModel(Model):
    '''
    represents a 2D lattice where agents live
    '''

    def __init__(self, height, width):
        '''
        Create a 2D lattice with strict borders where agents live
        The agents next state is first determined before updating the grid
        '''

        self._grid = Grid(height, width, torus=False)
        self._schedule = SimultaneousActivation(self)

        # self._grid.coord_iter()
        #  --> should really not return content + col + row
        #  -->but only col & row
        # for (contents, col, row) in self._grid.coord_iter():
        # replaced content with _ to appease linter
        for (_, col, row) in self._grid.coord_iter():
            cell = ColorCell((col, row), self, ColorCell.OPINIONS[random.randrange(0, 16)])
            self._grid.place_agent(cell, (col, row))
            self._schedule.add(cell)

        self.running = True

    def step(self):
        '''
        Advance the model one step.
        '''
        self._schedule.step()



    # the following is a temporary fix for the framework classes accessing model
    # attributes directly
    # I don't think it should
    #   --> it imposes upon the model builder to use the attributes names that
    #       the framework expects.
    #
    # Traceback included in docstrings

    @property
    def grid(self):
        """
        /mesa/visualization/modules/CanvasGridVisualization.py
        is directly accessing Model.grid
             76     def render(self, model):
             77         grid_state = defaultdict(list)
        ---> 78         for y in range(model.grid.height):
             79             for x in range(model.grid.width):
             80                 cell_objects = model.grid.get_cell_list_contents([(x, y)])

        AttributeError: 'ColorPatchModel' object has no attribute 'grid'
        """
        return self._grid

    @property
    def schedule(self):
        """
        mesa_ABM/examples_ABM/color_patches/mesa/visualization/ModularVisualization.py",
        line 278, in run_model
            while self.model.schedule.steps < self.max_steps and self.model.running:
        AttributeError: 'NoneType' object has no attribute 'steps'
        """
        return self._schedule
