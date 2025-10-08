"""Solara visualization related helper classes."""


class UserParam:
    """UserParam."""

    _ERROR_MESSAGE = "Missing or malformed inputs for '{}' Option '{}'"

    def maybe_raise_error(self, param_type, valid):  # noqa: D102
        if valid:
            return
        msg = self._ERROR_MESSAGE.format(param_type, self.label)
        raise ValueError(msg)


class Slider(UserParam):
    """A number-based slider input with settable increment.

    Example:
    slider_option = Slider("My Slider", value=123, min=10, max=200, step=0.1)

    Args:
        label: The displayed label in the UI
        value: The initial value of the slider
        min: The minimum possible value of the slider
        max: The maximum possible value of the slider
        step: The step between min and max for a range of possible values
        dtype: either int or float
    """

    def __init__(
        self,
        label="",
        value=None,
        min=None,
        max=None,
        step=1,
        dtype=None,
    ):
        """Initializes a slider.

        Args:
            label: The displayed label in the UI
            value: The initial value of the slider
            min: The minimum possible value of the slider
            max: The maximum possible value of the slider
            step: The step between min and max for a range of possible values
            dtype: either int or float
        """
        self.label = label
        self.value = value
        self.min = min
        self.max = max
        self.step = step

        # Validate option type to make sure values are supplied properly
        valid = not (self.value is None or self.min is None or self.max is None)
        self.maybe_raise_error("slider", valid)

        if dtype is None:
            self.is_float_slider = self._check_values_are_float(value, min, max, step)
        else:
            self.is_float_slider = dtype is float

    def _check_values_are_float(self, value, min, max, step):  # D103
        return any(isinstance(n, float) for n in (value, min, max, step))

    def get(self, attr):  # noqa: D102
        return getattr(self, attr)


class TextInput(UserParam):
    """A text input field for user-provided string values.

    Example:
        text_option = TextInput(
            "Dataset Path",
            value="data/input.csv",
            placeholder="Enter file path...",
        )

    Args:
        label: The displayed label in the UI
        value: The initial text value(converted to the string if not)
        placeholder: Optional placeholder text in the input field
        description: Optional tooltip or helper text
    """

    def __init__(self, label="", value="", placeholder="", description=None):
        self.label = label
        self.placeholder = placeholder
        self.description = description

        # convert any input to the string safely
        if value is None:
            self.value = ""
        else:
            self.value = str(value)

        # Always passes validation now
        valid = True
        self.maybe_raise_error("InputText", valid)  # matches solaraViz type name

    def get(self, attr):
        """Return attribute value (compatible with other UserParam types)."""
        return getattr(self, attr)
