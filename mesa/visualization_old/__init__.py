import contextlib

with contextlib.suppress(ImportError):
    from mesa_viz_tornado.ModularVisualization import *  # noqa
    from mesa_viz_tornado.modules import *  # noqa
    from mesa_viz_tornado.UserParam import *  # noqa
    from mesa_viz_tornado.TextVisualization import *  # noqa
