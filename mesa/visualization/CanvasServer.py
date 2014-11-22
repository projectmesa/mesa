'''
CanvasServer
============================================================================

A simple experimental Tornado server which renders a Grid or MultiGrid via 
HTML5 Canvas.

Consists of the following classes:

PageHandler: The handler for the visualization page, generated from a template.
SocketHandler: Handles the websocket connection between the client page and
                the server.
CanvasServer: The overall controller class which stores and controls
            the model and visualization instance.

In theory, CanvasServer does NOT need to be subclassed on a model-by-model
basis; it should be able to create a browser visualization for any Grid or 
MultiGrid model, with the appropriate portrayal function.

A CanvasServer is created using one class for the model, and a function which 
maps each grid object to a Portrayal. The new CanvasServer can also accept
arguments to pass to the first model instance. To go with the perennial
Schelling example, the following code

    def schelling_draw(agent):
        portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}
        portrayal["x"] = agent.x
        portrayal["y"] = agent.y
        if agent.type == 0:
            portrayal["color"] = "#AA0000"
        else:
            portrayal["color"] = "#0000AA"
        return portrayal

    server = CanvasServer(SchellingModel, schelling_draw, 500, 500,
        "Schelling", 10, 10, 0.8, 0.2, 3)

creates a CanvasServer visualizing a SchellingModel named "Schelling", which 
draws agents as circles (majorities as red, minorities as blue), on a 500x500
canvas, with 10, 10... , 3 as the default model parameters.

The server is launched using the launch() method. This runs the Tornado app,
which consists of PageHandler and SocketHandler. At the moment, the server runs
the entire model (up to a default max_steps) prior to actually serving the
data.
TODO: Make the model run a coroutine.

The client keeps track of what step it is showing. Clicking the Step button in
the browser sends a message requesting the viz_state corresponding to the next
step position, which is then sent back to the client via the websocket.

The websocket protocol is as follows:
Each message is a JSON object, with a "type" property which defines the rest of
the structure.

Server -> Client:
    Send over the model state to visualize:
    {
    "type": "viz_state",
    "data": [ [{"Shape": "circle", "x": 0, "y": 0, "r": 0.5, 
                "Color": "#AAAAAA", "Filled": "true", "Layer": 1}] 
            ]
             
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
'''
from collections import defaultdict
import os

import tornado.ioloop
import tornado.template
import tornado.web
import tornado.websocket
import tornado.escape

# Suppress several pylint warnings for this file.
# Attributes being defined outside of init is a Tornado feature.
# pylint: disable=attribute-defined-outside-init

class PageHandler(tornado.web.RequestHandler):
    '''
    Handler for the HTML template which holds the visualization.
    '''
    def initialize(self, controller):
        self.controller = controller
        path = os.path.dirname(__file__) + "/templates"
        loader = tornado.template.Loader(path)
        self.template = loader.load("canvas_template.html")

    def get(self):
        page = self.template.generate(
            port=self.controller.port,
            model_name=self.controller.model_name,
            canvas_height = self.controller.canvas_height,
            canvas_width = self.controller.canvas_width,
            grid_height = self.controller.grid_height,
            grid_width = self.controller.grid_width)
        self.write(page)


class SocketHandler(tornado.websocket.WebSocketHandler):
    '''
    Handler for websocket.
    '''
    def initialize(self, controller):
        self.controller = controller

    def open(self):
        if self.controller.verbose:
            print("Socket opened!")

    def on_message(self, message):
        '''
        Receiving a message from the websocket, parse, and act accordingly.
        '''
        if self.controller.verbose:
            print(message)
        msg = tornado.escape.json_decode(message)

        if msg["type"] == "get_step":
            step = int(msg["step"])
            if step < len(self.controller.viz_states):
                return_message = {"type": "viz_state"}
                return_message["data"] = self.controller.viz_states[step]
            else:
                return_message = {"type": "end"}
            self.write_message(return_message)

        elif msg["type"] == "reset":
            self.controller.reset()
            return_message = {"type": "viz_state"}
            return_message["data"] = self.controller.viz_states[0]

            self.write_message(return_message)
            self.controller.run_model()

        else:
            if self.controller.verbose:
                print("Unexpected message!")


class CanvasServer(object):
    '''
    Main class for handling the visualization web app.

    Currently assumes that the model object has a grid attribute.

    Attributes:
        verbose: (default True) Whether to write most events to the terminal
        model_name: Name to display in the browser. (defaults to "Mesa Model")

        model_cls: The class of the model to render.
        portrayal_method: Method which maps each object to a portrayal.
        
        port: (default 8888) Port to listen on.
        canvas_width, canvas_height: Pixels to draw the canvas on the page.
        grid_width, grid_height: Number of cells in the grid.
        multigrid: Boolean whether the grid is a MultiGrid or not.

        max_steps: Maximum number of steps to pre-run the model for.
        viz_states: List of dictionaries representing the rendering of the model
                    at each step.

        model_args: Tuple of positional arguments to pass to each new model obj.
        model_kwargs: Dictionary of keyword arguments to pass to each new model.

    '''

    verbose = True

    model_name = "Mesa Model"
    model_cls = None  # A model class
    portrayal_method = None
    port = 8888  # Port to listen on
    canvas_width = 500
    canvas_height = 500
    grid_height = 0
    grid_width = 0

    max_steps = 100
    viz_states = []

    model_args = ()
    model_kwargs = {}

    def __init__(self, model_cls, portrayal_method, canvas_height, canvas_width,
                 name="Mesa Model", *args, **kwargs):
        '''
        Create a new canvas visualization server.

        This server will render and control a model_cls model and render it as
        described in an associated portrayal_method.

        Args:
            model_cls: A model class to visualize
            portrayal_method: Function mapping objects to portrayals
            canvas_height, canvas_width: Pixels for canvas width, height
            name: A name for the model.
            *args, **kwargs: Default arguments to create a model with.
        '''
        self.model_name = name
        self.model_cls = model_cls
        self.portrayal_method = portrayal_method

        # TODO: Make this more elegant
        self.model_args = args
        self.model_kwargs = kwargs

        self.reset()
        self.grid_width = self.model.grid.width
        self.grid_height = self.model.grid.height

        self.application = tornado.web.Application([
            (r'/', PageHandler, {"controller": self}),
            (r'/ws', SocketHandler, {"controller": self})],
            static_path=os.path.dirname(__file__) + "/templates")

    def launch(self, port=8888):
        '''
        Launch the server and have it listen on the given port.
        '''
        self.port = port
        print("Launching server, listening on port", port)
        self.run_model()
        self.application.listen(port)
        tornado.ioloop.IOLoop.instance().start()

    def reset(self):
        '''
        Resets the model by creating a new instance of it, with the given args.
        '''
        self.model = self.model_cls(*self.model_args, **self.model_kwargs)
        self.viz_states = [self.get_viz()]

    def get_viz(self):
        '''
        Turn the current visualization state into a text dictionary.
        '''
        viz_state = defaultdict(list)
        for y in range(self.grid_height):
            for x in range(self.grid_height):
                # TODO: Have this work for multigrid
                portrayal = self.portrayal_method(self.model.grid[y][x])
                if portrayal:
                    viz_state[portrayal["Layer"]].append(portrayal)
        return viz_state

    def run_model(self):
        '''
        Run the model forward and store each viz state.
        #TODO: Have this run concurrently (I think) inside the event loop?
        '''
        while self.model.schedule.steps < self.max_steps and self.model.running:
            self.model.step()
            self.viz_states.append(self.get_viz())
        if self.verbose:
            print("Model steps:", self.model.schedule.steps)
