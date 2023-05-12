import numbers

NUMBER = "number"
CHECKBOX = "checkbox"
CHOICE = "choice"
SLIDER = "slider"
STATIC_TEXT = "static_text"


class UserParam:
    _ERROR_MESSAGE = "Missing or malformed inputs for '{}' Option '{}'"

    @property
    def json(self):
        result = self.__dict__.copy()
        result["value"] = result.pop(
            "_value"
        )  # Return _value as value, value is the same
        return result

    def maybe_raise_error(self, valid):
        if not valid:
            msg = self._ERROR_MESSAGE.format(self.param_type, self.name)
            raise ValueError(msg)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Slider(UserParam):
    """
    A number-based slider input with settable increment.

    Example:

    slider_option = Slider("My Slider", value=123, min_value=10, max_value=200, step=0.1)
    """

    def __init__(
        self,
        name="",
        value=None,
        min_value=None,
        max_value=None,
        step=1,
        description=None,
    ):
        self.param_type = SLIDER
        self.name = name
        self._value = value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.description = description

        # Validate option type to make sure values are supplied properly
        valid = not (
            self.value is None or self.min_value is None or self.max_value is None
        )
        self.maybe_raise_error(valid)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self._value < self.min_value:
            self._value = self.min_value
        elif self._value > self.max_value:
            self._value = self.max_value


class Checkbox(UserParam):
    """
    Boolean checkbox.

    Example:

    boolean_option = Checkbox('My Boolean', True)
    """

    def __init__(self, name="", value=None, description=None):
        self.param_type = CHECKBOX
        self.name = name
        self._value = value
        self.description = description

        # Validate option type to make sure values are supplied properly
        valid = isinstance(self.value, bool)
        self.maybe_raise_error(valid)


class Choice(UserParam):
    """
    String-based dropdown input, for selecting choices within a model

    Example:
    choice_option = Choice(
        'My Choice',
        value='Default choice',
        choices=['Default Choice', 'Alternate Choice']
    )
    """

    def __init__(self, name="", value=None, choices=None, description=None):
        self.param_type = CHOICE
        self.name = name
        self._value = value
        self.choices = choices
        self.description = description

        # Validate option type to make sure values are supplied properly
        valid = not (self.value is None or len(self.choices) == 0)
        self.maybe_raise_error(valid)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self._value not in self.choices:
            print(
                "Selected choice value not in available choices, selected first choice from 'choices' list"
            )
            self._value = self.choices[0]


class StaticText(UserParam):
    """
    A non-input textbox for displaying model info.

    Example:
    static_text = StaticText("This is a descriptive textbox")
    """

    def __init__(self, value=None):
        self.param_type = STATIC_TEXT
        self._value = value
        valid = isinstance(self.value, str)
        self.maybe_raise_error(valid)


class NumberInput(UserParam):
    """
    a simple numerical input

    Example:
    number_option = NumberInput("My Number", value=123)
    """

    def __init__(self, name="", value=None, description=None):
        self.param_type = NUMBER
        self.name = name
        self._value = value
        valid = isinstance(self.value, numbers.Number)
        self.maybe_raise_error(valid)
