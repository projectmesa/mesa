'''
UserParam classes allow model visualization developers to set a model parameter
to be interactive, so that the user can change it within the visualization
while the model is running.

Setting a model parameter equal to a UserParam object tells Mesa to create a
control in the GUI for that value, and to change that value when resetting
the model.
'''

class UserParam:
    '''
    Base class for a user-settable parameter; assumes that the parameter is
    numeric.
    '''

    def __init__(self, name, starting_value, min_value, max_value, step=1):
        '''
        Create a new numeric user-settable parameter.
        '''

        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.current_value = starting_value

    def get_value(self):
        '''
        Get the parameter's current value
        '''
        return self.current_value

    def update_value(self, new_value):
        '''
        Update the current value, only if it is valid.
        '''
        if (self.min_value <= new_value <= self.max_value):
            # Removing step validation for now because of floating point issues
            self.current_value = new_value
        else:
            raise Exception("Incorrect input value")



