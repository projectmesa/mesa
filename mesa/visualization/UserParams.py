'''
UserParam classes allow model visualization developers to set a model parameter
to be interactive, so that the user can change it within the visualization
while the model is running.

Setting a model parameter equal to a UserParam object tells Mesa to create a
control in the GUI for that value, and to change that value when resetting
the model.


'''
import tornado.escape


class UserParam:
    '''
    Base class for a user-settable numeric parameter.
    '''
    JS_CODE = 'add(params, "{name}").min({min}).max({max}).step({step});'

    def __init__(self, start_value, min_value, max_value, step=1, label=None):
        '''
        Create a new numeric user-settable parameter.

        '''

        self.name = None
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.current_value = start_value

    def set_name(self, name):
        '''
        Update the name, which is tied to the model parameter keyword.
        '''
        self.name = name
        if self.label is None:
            self.label = name

    def get_code(self):
        '''
        Get JavaScript code to add to the GUI.
        '''
        code = self.JS_CODE.format(name=self.name, min=self.min_value,
                                   max=self.max_value, step=self.step)
        return code
        # return tornado.escape.xhtml_unescape(code)

    def get_value(self):
        '''
        Get the parameter's current value
        '''
        return self.current_value

    def get_js_value(self):
        '''
        Return the parameter's current value for insertion into JavaScript
        '''
        return self.get_value()

    def update_value(self, new_value):
        '''
        Update the current value, only if it is valid.
        '''
        if (self.min_value <= new_value <= self.max_value):
            # Removing step validation for now because of floating point issues
            self.current_value = new_value
        else:
            raise Exception("Incorrect input value")


class UserOption(UserParam):
    '''
    User-settable parameter for discrete values.
    '''

    JS_CODE = 'add(params, "{name}", {all_values});'

    def __init__(self, start_value, all_values, label=None):
        '''
        Create a new, discrete parameter.
        '''
        self.current_value = start_value
        self.all_values = all_values
        self.label = label

    def get_code(self):
        '''
        Get JavaScript code to add to the GUI.
        '''
        code = self.JS_CODE.format(name=self.name,
                                   all_values=str(self.all_values))
        return code

    def get_js_value(self):
        '''
        Check if the option is a string, and return accordingly.
        '''
        if type(self.current_value) is str:
            return '"{}"'.format(self.current_value)
        else:
            return self.current_value

    def update_value(self, new_value):
        '''
        Validate and update new value.
        '''
        if new_value in self.all_values:
            self.current_value = new_value
        else:
            raise Exception("Incorrect input value")
