# -*- coding: utf-8 -*-
"""
ModularServer
=============

A visualization server which renders a model via one or more elements.

The concept for the modular visualization server as follows:
A visualization is composed of VisualizationElements, each of which defines how
to generate some visualization from a model instance and render it on the
client. VisualizationElements may be anything from a simple text display to
a multilayered HTML5 canvas.

The actual server is launched with one or more VisualizationElements;
it runs the model object through each of them, generating data to be sent to
the client. The client page is also generated based on the JavaScript code
provided by each element.

This file consists of the following classes:

VisualizationElement: Parent class for all other visualization elements, with
                      the minimal necessary options.
PageHandler: The handler for the visualization page, generated from a template
             and built from the various visualization elements.
SocketHandler: Handles the websocket connection between the client page and
                the server.
ModularServer: The overall visualization application class which stores and
               controls the model and visualization instance.


ModularServer should *not* need to be subclassed on a model-by-model basis; it
should be primarily a pass-through for VisualizationElement subclasses, which
define the actual visualization specifics.

For example, suppose we have created two visualization elements for our model,
called canvasvis and graphvis; we would launch a server with:

    server = ModularServer(MyModel, [canvasvis, graphvis], name="My Model")
    server.launch()

The client keeps track of what step it is showing. Clicking the Step button in
the browser sends a message requesting the viz_state corresponding to the next
step position, which is then sent back to the client via the websocket.

The websocket protocol is as follows:
Each message is a JSON object, with a "type" property which defines the rest of
the structure.

Server -> Client:
    Send over the model state to visualize.
    Model state is a list, with each element corresponding to a div; each div
    is expected to have a render function associated with it, which knows how
    to render that particular data. The example below includes two elements:
    the first is data for a CanvasGrid, the second for a raw text display.

    {
    "type": "viz_state",
    "data": [{0:[ {"Shape": "circle", "x": 0, "y": 0, "r": 0.5,
                "Color": "#AAAAAA", "Filled": "true", "Layer": 0,
                "text": 'A', "text_color": "white" }]},
            "Shape Count: 1"]
    }

    Informs the client that the model is over.
    {"type": "end"}

Client -> Server:
    Reset the model.
    TODO: Allow this to come with parameters
    {
    "type": "reset"
    }

    Get a given state.
    {
    "type": "get_step",
    "step:" index of the step to get.
    }

"""
import os

import tornado.autoreload
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.escape
import tornado.gen

import webbrowser

# Suppress several pylint warnings for this file.
# Attributes being defined outside of init is a Tornado feature.
# pylint: disable=attribute-defined-outside-init


class VisualizationElement:
    """
    Defines an element of the visualization.

    Attributes:
        package_includes: A list of external JavaScript files to include that
                          are part of the Mesa packages.
        local_includes: A list of JavaScript files that are local to the
                        directory that the server is being run in.
        js_code: A JavaScript code string to instantiate the element.

    Methods:
        render: Takes a model object, and produces JSON data which can be sent
                to the client.

    """

    package_includes = []
    local_includes = []
    js_code = ''
    render_args = {}

    def __init__(self):
        pass

    def render(self, model):
        """ Build visualization data from a model object.

        Args:
            model: A model object

        Returns:
            A JSON-ready object.

        """
        return "<b>VisualizationElement goes here</b>."

# =============================================================================
# Actual Tornado code starts here:


class PageHandler(tornado.web.RequestHandler):
    """ Handler for the HTML template which holds the visualization. """

    def get(self):
        elements = self.application.visualization_elements
        for i, element in enumerate(elements):
            element.index = i
        self.render("modular_template.html", port=self.application.port,
                    model_name=self.application.model_name,
                    package_includes=self.application.package_includes,
                    local_includes=self.application.local_includes,
                    scripts=self.application.js_code)


class SocketHandler(tornado.websocket.WebSocketHandler):
    """ Handler for websocket. """
    def open(self):
        if self.application.verbose:
            print("Socket opened!")

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        """ Receiving a message from the websocket, parse, and act accordingly.

        """
        if self.application.verbose:
            print(message)
        msg = tornado.escape.json_decode(message)

        if msg["type"] == "get_step":
            if not self.application.model.running:
                self.write_message({"type": "end"})
            else:
                self.application.model.step()
                self.write_message({"type": "viz_state",
                        "data": self.application.render_model()})

        elif msg["type"] == "reset":
            self.application.reset_model()
            self.write_message({"type": "viz_state",
                    "data": self.application.render_model()})

        else:
            if self.application.verbose:
                print("Unexpected message!")


class ModularServer(tornado.web.Application):
    """ Main visualization application. """
    verbose = True

    model_name = "Mesa Model"
    model_cls = None  # A model class
    portrayal_method = None
    port = 8521  # Default port to listen on
    canvas_width = 500
    canvas_height = 500
    grid_height = 0
    grid_width = 0

    max_steps = 100000

    model_args = ()
    model_kwargs = {}

    # Handlers and other globals:
    page_handler = (r'/', PageHandler)
    socket_handler = (r'/ws', SocketHandler)
    static_handler = (r'/static/(.*)', tornado.web.StaticFileHandler,
                      {"path": os.path.dirname(__file__) + "/templates"})
    local_handler = (r'/local/(.*)', tornado.web.StaticFileHandler,
                     {"path": ''})

    handlers = [page_handler, socket_handler, static_handler, local_handler]

    settings = {"debug": True,
                "autoreload": False,
                "template_path": os.path.dirname(__file__) + "/templates"}

    def __init__(self, model_cls, visualization_elements, name="Mesa Model",
                 *args, **kwargs):
        """ Create a new visualization server with the given elements. """
        # Prep visualization elements:
        self.visualization_elements = visualization_elements
        self.package_includes = set()
        self.local_includes = set()
        self.js_code = []
        for element in self.visualization_elements:
            for include_file in element.package_includes:
                self.package_includes.add(include_file)
            for include_file in element.local_includes:
                self.local_includes.add(include_file)
            self.js_code.append(element.js_code)

        # Initializing the model
        self.model_name = name
        self.model_cls = model_cls

        self.model_args = args
        self.model_kwargs = kwargs
        self.reset_model()

        # Initializing the application itself:
        super().__init__(self.handlers, **self.settings)

    def reset_model(self):
        """ Reinstantiate the model object, using the current parameters. """
        self.model = self.model_cls(*self.model_args, **self.model_kwargs)

    def render_model(self):
        """ Turn the current state of the model into a dictionary of
        visualizations

        """
        visualization_state = []
        for element in self.visualization_elements:
            element_state = element.render(self.model)
            visualization_state.append(element_state)
        return visualization_state

    def launch(self, port=None):
        """ Run the app. """
        startLoop = not tornado.ioloop.IOLoop.initialized()
        if port is not None:
            self.port = port
        url = 'http://127.0.0.1:{PORT}'.format(PORT=self.port)
        print('Interface starting at {url}'.format(url=url))
        self.listen(self.port)
        webbrowser.open(url)
        tornado.autoreload.start()
        if startLoop:
            tornado.ioloop.IOLoop.instance().start()
