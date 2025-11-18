"""Utilities used across mesa."""

import warnings
from functools import wraps


def deprecate_kwarg(name: str):
    def inner_wrapper(method):
        """Deprecation warning wrapper for seed kwarg."""

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            """Inner function."""
            if name in kwargs:
                warnings.warn(
                    f"The use of {name} is deprecated, please use rng instead",
                    FutureWarning,
                    stacklevel=2,
                )

            return method(self, *args, **kwargs)

        return wrapper

    return inner_wrapper
