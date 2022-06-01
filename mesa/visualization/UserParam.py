from warnings import warn
import numbers


NUMBER = "number"
CHECKBOX = "checkbox"
CHOICE = "choice"
SLIDER = "slider"
STATIC_TEXT = "static_text"


class UserSettableParameter:
    """A class for providing options to a visualization for a given parameter.

    UserSettableParameter can be used instead of keyword arguments when specifying model parameters in an
    instance of a `ModularServer` so that the parameter can be adjusted in the UI without restarting the server.

    Validation of correctly-specified params happens on startup of a `ModularServer`. Each param is handled
    individually in the UI and sends callback events to the server when an option is updated. That option is then
    re-validated, in the `value.setter` property method to ensure input is correct from the UI to `reset_model`
    callback.

    Parameter types include:
        - 'number' - a simple numerical input
        - 'checkbox' - boolean checkbox
        - 'choice' - String-based dropdown input, for selecting choices within a model
        - 'slider' - A number-based slider input with settable increment
        - 'static_text' - A non-input textbox for displaying model info.

    Examples:

    # Simple number input
    number_option = UserSettableParameter('number', 'My Number', value=123)

    # Checkbox input
    boolean_option = UserSettableParameter('checkbox', 'My Boolean', value=True)

    # Choice input
    choice_option = UserSettableParameter('choice', 'My Choice', value='Default choice',
                                          choices=['Default Choice', 'Alternate Choice'])

    # Slider input
    slider_option = UserSettableParameter('slider', 'My Slider', value=123, min_value=10, max_value=200, step=0.1)

    # Static text
    static_text = UserSettableParameter('static_text', value="This is a descriptive textbox")
    """

    NUMBER = NUMBER
    CHECKBOX = CHECKBOX
    CHOICE = CHOICE
    SLIDER = SLIDER
    STATIC_TEXT = STATIC_TEXT

    TYPES = (NUMBER, CHECKBOX, CHOICE, SLIDER, STATIC_TEXT)

    _ERROR_MESSAGE = "Missing or malformed inputs for '{}' Option '{}'"

    def __init__(
        self,
        param_type=None,
        name="",
        value=None,
        min_value=None,
        max_value=None,
        step=1,
        choices=None,
        description=None,
    ):

        warn(
            "UserSettableParameter is deprecated in favor of UserParam objects "
            "such as Slider, Checkbox, Choice, StaticText, NumberInput. "
            "See the examples folder for how to use them. "
            "UserSettableParameter will be removed in the next major release."
        )
        if choices is None:
            choices = list()
        if param_type not in self.TYPES:
            raise ValueError(f"{param_type} is not a valid Option type")
        self.param_type = param_type
        self.name = name
        self._value = value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.choices = choices
        self.description = description

        # Validate option types to make sure values are supplied properly
        msg = self._ERROR_MESSAGE.format(self.param_type, name)
        valid = True

        if self.param_type == self.NUMBER:
            valid = not (self.value is None)

        elif self.param_type == self.SLIDER:
            valid = not (
                self.value is None or self.min_value is None or self.max_value is None
            )

        elif self.param_type == self.CHOICE:
            valid = not (self.value is None or len(self.choices) == 0)

        elif self.param_type == self.CHECKBOX:
            valid = isinstance(self.value, bool)

        elif self.param_type == self.STATIC_TEXT:
            valid = isinstance(self.value, str)

        if not valid:
            raise ValueError(msg)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self.param_type == self.SLIDER:
            if self._value < self.min_value:
                self._value = self.min_value
            elif self._value > self.max_value:
                self._value = self.max_value
        elif self.param_type == self.CHOICE:
            if self._value not in self.choices:
                print(
                    "Selected choice value not in available choices, selected first choice from 'choices' list"
                )
                self._value = self.choices[0]

    @property
    def json(self):
        result = self.__dict__.copy()
        result["value"] = result.pop(
            "_value"
        )  # Return _value as value, value is the same
        return result


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
