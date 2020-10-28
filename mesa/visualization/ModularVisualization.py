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

    Informs the client of the current model's parameters
    {
    "type": "model_params",
    "params": 'dict' of model params, (i.e. {arg_1: val_1, ...})
    }

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

    Submit model parameter updates
    {
    "type": "submit_params",
    "param": name of model parameter
    "value": new value for 'param'
    }

    Get the model's parameters
    {
    "type": "get_params"
    }

"""
import os
import sys
import tornado.autoreload
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.escape
import tornado.gen
import webbrowser

from mesa.visualization.UserParam import UserSettableParameter

template_path = os.path.join(
    os.path.dirname(sys.modules["mesa.visualization"].__file__), "templates"
)

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
    js_code = ""
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
def reset_model(model_cls, model_kwargs):
    """ Reinstantiate the model object, using the current parameters. """

    model_params = {}
    for key, val in model_kwargs.items():
        if isinstance(val, UserSettableParameter):
            if (
                val.param_type == "static_text"
            ):  # static_text is never used for setting params
                continue
            model_params[key] = val.value
        else:
            model_params[key] = val

    model = model_cls(**model_params)

    return model


def render_model(model, visualization_elements):
    """ Turn the current state of the model into a dictionary of
    visualizations

    """
    visualization_state = []
    for element in visualization_elements:
        element_state = element.render(model)
        visualization_state.append(element_state)
    return visualization_state


def user_params(model_kwargs):
    result = {}
    for param, val in model_kwargs.items():
        if isinstance(val, UserSettableParameter):
            result[param] = val.json

    return result


class PageHandler(tornado.web.RequestHandler):
    """ Handler for the HTML template which holds the visualization. """

    def get(self):
        elements = self.application.visualization_elements
        for i, element in enumerate(elements):
            element.index = i
        self.render(
            "modular_template.html",
            port=self.application.port,
            model_name=self.application.model_name,
            description=self.application.description,
            package_includes=self.application.package_includes,
            local_includes=self.application.local_includes,
            scripts=self.application.js_code,
        )


class SocketHandler(tornado.websocket.WebSocketHandler):
    """
    Handler for websocket.

    Each websocket creates a new instance of the model and renders its
    output to the page. This allows you to have multiple tabs open to
    the same server, each running its own version of the model.
    """

    def open(self):
        self.model_kwargs = self.application.model_kwargs.copy()
        self.model = reset_model(self.application.model_cls, self.model_kwargs)
        if self.application.verbose:
            print("Socket opened!")
            print("Model ID:", id(self.model))
        self.write_message(
            {"type": "model_params", "params": user_params(self.model_kwargs)}
        )

    def check_origin(self, origin):
        return True

    @property
    def viz_state_message(self):
        return {
            "type": "viz_state",
            "data": render_model(self.model, self.application.visualization_elements),
        }

    def on_message(self, message):
        """ Receiving a message from the websocket, parse, and act accordingly.

        """
        if self.application.verbose:
            print(message)
        msg = tornado.escape.json_decode(message)

        if msg["type"] == "get_step":
            if not self.model.running:
                self.write_message({"type": "end"})
            else:
                self.model.step()
                self.write_message(self.viz_state_message)

        elif msg["type"] == "reset":
            self.model = reset_model(self.application.model_cls, self.model_kwargs)
            self.write_message(self.viz_state_message)

        elif msg["type"] == "submit_params":
            param = msg["param"]
            value = msg["value"]

            # Is the param editable?
            if param in user_params(self.model_kwargs):
                if isinstance(self.model_kwargs[param], UserSettableParameter):
                    self.model_kwargs[param].value = value
                else:
                    self.model_kwargs[param] = value

        else:
            if self.application.verbose:
                print("Unexpected message!")


class ModularServer(tornado.web.Application):
    """ Main visualization application. """

    verbose = True

    port = 8521  # Default port to listen on
    max_steps = 100000

    # Handlers and other globals:
    page_handler = (r"/", PageHandler)
    socket_handler = (r"/ws", SocketHandler)
    health_handler = (r"/healthz", tornado.web.ErrorHandler, {"status_code": 200})
    static_handler = (
        r"/static/(.*)",
        tornado.web.StaticFileHandler,
        {"path": template_path},
    )
    local_handler = (r"/local/(.*)", tornado.web.StaticFileHandler, {"path": ""})

    handlers = [
        page_handler,
        socket_handler,
        health_handler,
        static_handler,
        local_handler,
    ]

    settings = {
        "debug": True,
        "autoreload": False,
        "template_path": template_path,
    }

    EXCLUDE_LIST = ("width", "height")

    def __init__(
        self, model_cls, visualization_elements, name="Mesa Model", model_params={}
    ):
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
        self.description = "No description available"
        if hasattr(model_cls, "description"):
            self.description = model_cls.description
        elif model_cls.__doc__ is not None:
            self.description = model_cls.__doc__

        self.model_kwargs = model_params

        # Initializing the application itself:
        super().__init__(self.handlers, **self.settings)

    def launch(self, port=None, open_browser=True):
        """ Run the app. """
        if port is not None:
            self.port = port
        url = "http://127.0.0.1:{PORT}".format(PORT=self.port)
        print("Interface starting at {url}".format(url=url))
        self.listen(self.port)
        if open_browser:
            webbrowser.open(url)
        tornado.autoreload.start()
        tornado.ioloop.IOLoop.current().start()
