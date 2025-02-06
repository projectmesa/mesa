"""Experimental features package for Mesa.

This package contains modules that are under active development and testing. These
features are provided to allow early access and feedback from the Mesa community, but
their APIs may change between releases without following semantic versioning.

Current experimental modules:
    cell_space: Alternative API for discrete spaces with cell-centric functionality
    devs: Discrete event simulation system for scheduling events at arbitrary times
    mesa_signals: Reactive programming capabilities for tracking state changes

Notes:
    - Features in this package may be changed or removed without notice
    - APIs are not guaranteed to be stable between releases
    - Features graduate from experimental status once their APIs are stabilized
"""

from mesa.experimental import cell_space, continuous_space, devs, mesa_signals

__all__ = ["cell_space", "continuous_space", "devs", "mesa_signals"]
