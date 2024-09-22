"""A signals implementation for Python."""

from __future__ import annotations

from ._core import Signal, batch, computed, effect
from ._version import __version__


def load_ipython_extension(ipython):
    """Load the IPython extension.

    `%load_ext signals` will load the extension and enable the `%%effect` cell magic.

    Parameters
    ----------
    ipython : IPython.core.interactiveshell.InteractiveShell
        The IPython shell instance.
    """
    from ._cellmagic import load_ipython_extension

    load_ipython_extension(ipython)
