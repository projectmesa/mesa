"""helper functions and classes for mesa signals."""

import weakref

__all__ = [
    "AttributeDict",
    "create_weakref",
]



class AttributeDict(dict):
    """A dict with attribute like access.

    Each value can be accessed as if it were an attribute with its key as attribute name

    """

    # I want our signals to act like traitlet signals, so this is inspired by trailets Bunch
    # and some stack overflow posts.
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError as e:
            # we need to go from key error to attribute error
            raise AttributeError(key) from e

    def __dir__(self):
        # allows us to easily access all defined attributes
        names = dir({})
        names.extend(self.keys())
        return names


def create_weakref(item, callback=None):
    """Helper function to create a correct weakref for any item."""
    if hasattr(item, "__self__"):
        ref = weakref.WeakMethod(item, callback)
    else:
        ref = weakref.ref(item, callback)
    return ref


if __name__ == "__main__":
    a = dict(a=1, b=2)
    b = AttributeDict(a)
    print(dir(a))
    print(dir(b))
