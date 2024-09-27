import weakref

__all__ = ["create_weakref"]


def create_weakref(item, callback=None):
    """Helper function to create a correct weakref for any item"""
    if hasattr(item, "__self__"):
        ref = weakref.WeakMethod(item, callback)
    else:
        ref = weakref.ref(item, callback)
    return ref
