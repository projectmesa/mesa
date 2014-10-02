'''
Text Visualization
=======================

Base class for an ASCII-only visualization of a model.
'''

class TextVisualization(object):
    '''
    ASCII-Only visualization of a model.
    '''

    model = None

    def __init__(self, model):
        '''
        Create a new Text Visualization object.
        '''
        self.model = model