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
import asyncio
import os
import platform
import webbrowser

import tornado.autoreload
import tornado.escape
import tornado.gen
import tornado.ioloop
import tornado.web
import tornado.websocket

from mesa.visualization.UserParam import UserParam, UserSettableParameter

# Suppress several pylint warnings for this file.
# Attributes being defined outside of init is a Tornado feature.
# pylint: disable=attribute-defined-outside-init

# Change the event loop policy for windows
if platform.system() == "Windows" and platform.python_version_tuple() >= ("3", "7"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

D3_JS_FILE = "external/d3-7.4.3.min.js"
CHART_JS_FILE = "external/chart-3.6.1.min.js"


def is_user_param(val):
    return isinstance(val, UserSettableParameter) or issubclass(
        val.__class__, UserParam
    )


class VisualizationElement:
    """
    Defines an element of the visualization.

    Attributes:
        package_includes: A list of external JavaScript and CSS files to
                          include that are part of the Mesa packages.
        local_includes: A list of JavaScript and CSS files that are local to
                        the directory that the server is being run in.
        js_code: A JavaScript code string to instantiate the element.
        local_dir: A full path to the directory containing the local includes.
                   If a relative path is given, it is relative to the working
                   directory where the server is being run. If an absolute path
                   is given, it is used as-is. Default is the current working
                   directory.

    Methods:
        render: Takes a model object, and produces JSON data which can be sent
                to the client.
    """

    package_includes = []
    local_includes = []
    js_code = ""
    render_args = {}
    local_dir = ""

    def __init__(self):
        pass

    def render(self, model):
        """Build visualization data from a model object.

        Args:
            model: A model object

        Returns:
            A JSON-ready object.
        """
        return "<b>VisualizationElement goes here</b>."


class TextElement(VisualizationElement):
    """
    Module for drawing live-updating text.
    """

    package_includes = ["TextModule.js"]
    js_code = "elements.push(new TextModule());"


# =============================================================================
# Actual Tornado code starts here:


class PageHandler(tornado.web.RequestHandler):
    """Handler for the HTML template which holds the visualization."""

    def get(self):
        elements = self.application.visualization_elements
        for i, element in enumerate(elements):
            element.index = i
        self.render(
            "modular_template.html",
            port=self.application.port,
            model_name=self.application.model_name,
            description=self.application.description,
            package_js_includes=self.application.package_js_includes,
            package_css_includes=self.application.package_css_includes,
            local_js_includes=self.application.local_js_includes,
            local_css_includes=self.application.local_css_includes,
            scripts=self.application.js_code,
        )


class SocketHandler(tornado.websocket.WebSocketHandler):
    """Handler for websocket."""

    def open(self):
        if self.application.verbose:
            print("Socket opened!")
        self.write_message(
            {"type": "model_params", "params": self.application.user_params}
        )

    def check_origin(self, origin):
        return True

    @property
    def viz_state_message(self):
        return {"type": "viz_state", "data": self.application.render_model()}

    def on_message(self, message):
        """Receiving a message from the websocket, parse, and act accordingly."""
        if self.application.verbose:
            print(message)
        msg = tornado.escape.json_decode(message)

        if msg["type"] == "get_step":
            if not self.application.model.running:
                self.write_message({"type": "end"})
            else:
                self.application.model.step()
                self.write_message(self.viz_state_message)

        elif msg["type"] == "reset":
            self.application.reset_model()
            self.write_message(self.viz_state_message)

        elif msg["type"] == "submit_params":
            param = msg["param"]
            value = msg["value"]

            # Is the param editable?
            if param in self.application.user_params:
                if is_user_param(self.application.model_kwargs[param]):
                    self.application.model_kwargs[param].value = value
                else:
                    self.application.model_kwargs[param] = value

        else:
            if self.application.verbose:
                print("Unexpected message!")


class ModularServer(tornado.web.Application):
    """Main visualization application."""

    EXCLUDE_LIST = ("width", "height")

    def __init__(
        self,
        model_cls,
        visualization_elements,
        name="Mesa Model",
        model_params=None,
        port=None,
    ):
        """
        Args:
            model_cls: Mesa model class
            visualization_elements: visualisation elements
            name: A String for the model name
            port: Port the webserver listens to (int)
                Order of configuration:
                1. Parameter to ModularServer.launch
                2. Parameter to ModularServer()
                3. Environment var PORT
                4. Default value (8521)
            model_params: A dict of model parameters
        """

        self.verbose = True
        self.max_steps = 100000

        if port is not None:
            self.port = port
        else:
            # Default port to listen on
            self.port = int(os.getenv("PORT", 8521))

        # Handlers and other globals:
        page_handler = (r"/", PageHandler)
        socket_handler = (r"/ws", SocketHandler)
        static_handler = (
            r"/static/(.*)",
            tornado.web.StaticFileHandler,
            {"path": os.path.dirname(__file__) + "/templates"},
        )
        custom_handler = (
            r"/local/custom/(.*)",
            tornado.web.StaticFileHandler,
            {"path": ""},
        )
        self.handlers = [page_handler, socket_handler, static_handler, custom_handler]

        self.settings = {
            "debug": True,
            "autoreload": False,
            "template_path": os.path.dirname(__file__) + "/templates",
        }

        """Create a new visualization server with the given elements."""
        if model_params is None:
            model_params = {}
        # Prep visualization elements:
        self.visualization_elements = self._auto_convert_functions_to_TextElements(
            visualization_elements
        )
        self.package_js_includes = set()
        self.package_css_includes = set()
        self.local_js_includes = set()
        self.local_css_includes = set()
        self.js_code = []
        for element in self.visualization_elements:
            for include_file in element.package_includes:
                if self._is_stylesheet(include_file):
                    self.package_css_includes.add(include_file)
                else:
                    self.package_js_includes.add(include_file)
            if element.local_includes:
                mapped_local_dir = element.__class__.__name__
                element_file_handler = (
                    rf"/local/{mapped_local_dir}/(.*)",
                    tornado.web.StaticFileHandler,
                    {"path": element.local_dir},
                )
                self.handlers.append(element_file_handler)
                for include_file in element.local_includes:
                    include_file_path = f"{mapped_local_dir}/{include_file}"
                    if self._is_stylesheet(include_file):
                        self.local_css_includes.add(include_file_path)
                    else:
                        self.local_js_includes.add(include_file_path)
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
        self.reset_model()

        # Initializing the application itself:
        super().__init__(self.handlers, **self.settings)

    @property
    def user_params(self):
        result = {}
        for param, val in self.model_kwargs.items():
            if is_user_param(val):
                result[param] = val.json

        return result

    def reset_model(self):
        """Reinstantiate the model object, using the current parameters."""

        model_params = {}
        for key, val in self.model_kwargs.items():
            if is_user_param(val):
                if val.param_type == "static_text":
                    # static_text is never used for setting params
                    continue
                model_params[key] = val.value
            else:
                model_params[key] = val

        self.model = self.model_cls(**model_params)
        # We specify the `running` attribute here so that the user doesn't have
        # to define it explicitly in their model's __init__.
        self.model.running = True

    def render_model(self):
        """Turn the current state of the model into a dictionary of
        visualizations
        """
        visualization_state = []
        for element in self.visualization_elements:
            element_state = element.render(self.model)
            visualization_state.append(element_state)
        return visualization_state

    def launch(self, port=None, open_browser=True):
        """Run the app."""
        if port is not None:
            self.port = port
        url = f"http://127.0.0.1:{self.port}"
        print(f"Interface starting at {url}")
        self.listen(self.port)
        if open_browser:
            webbrowser.open(url)
        tornado.autoreload.start()
        tornado.ioloop.IOLoop.current().start()

    @staticmethod
    def _is_stylesheet(filename):
        return filename.lower().endswith(".css")

    def _auto_convert_fn_to_TextElement(self, x):
        """
        Automatically convert a function to a TextElement object.
        See https://github.com/projectmesa/mesa/issues/1233.
        """

        # Note: a class constructor is also a callable.
        if not callable(x):
            # i.e. not a function
            return x

        class MyTextElement(TextElement):
            def render(self, model):
                return x(model)

        return MyTextElement()

    def _auto_convert_functions_to_TextElements(self, visualization_elements):
        out_elements = [
            self._auto_convert_fn_to_TextElement(e) for e in visualization_elements
        ]
        return out_elements
