
class Option:
    """ A class for providing options to a visualization for a given parameter.
        Validation of correctly-specified options happens are startup.
        Each Option is handled individually in the UI and sends callback events
        to the server when an option is updated. That option is then re-validated,
        in the `value.setter` property method, to ensure input is correct from UI
        to model resets.

        Option types include:
            - 'number' - simple numerical input.
            - 'checkbox' - boolean input
            - 'choice' - String-based dropdown input

     """

    NUMBER = 'number'
    CHECKBOX = 'checkbox'
    CHOICE = 'choice'
    SLIDER = 'slider'

    TYPES = (NUMBER, CHECKBOX, CHOICE, SLIDER)

    _ERROR_MESSAGE = "Missing or malformed inputs for '{}' Option '{}'"

    def __init__(
        self, option_type=None, name='', value=None, min_value=None, max_value=None,
            step=1, choices=list()
    ):
        if option_type not in self.TYPES:
            raise ValueError("{} is not a valid Option type".format(option_type))
        self.option_type = option_type
        self.name = name
        self._value = value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.choices = choices

        # Validate option types to make sure values are supplied properly
        msg = self._ERROR_MESSAGE.format(self.option_type, name)
        valid = True

        if self.option_type == self.NUMBER:
            valid = not (self.value is None)

        elif self.option_type == self.SLIDER:
            valid = not (self.value is None or self.min_value is None or self.max_value is None)

        elif self.option_type == self.CHOICE:
            valid = not (self.value is None or len(self.choices) == 0)

        elif self.option_type == self.CHECKBOX:
            valid = isinstance(self.value, bool)

        if not valid:
            raise ValueError(msg)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self.option_type == self.SLIDER:
            if self._value < self.min_value:
                self._value = self.min_value
            elif self._value > self.max_value:
                self._value = self.max_value
        elif self.option_type == self.CHOICE:
            if self._value not in self.choices:
                print("Selected choice value not in available choices, selected first choice from 'choices' list")
                self._value = self.choices[0]

    @property
    def json(self):
        result = self.__dict__.copy()
        result['value'] = result.pop('_value')  # Return _value as value, lvalue is the same
        return result
