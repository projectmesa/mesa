'''
TextServer
============================================================================

A simple experimental Tornado server which renders an arbitrary ASCII 
visualization in the browser.

Consists of the following classes:

PageHandler: The handler for the visualization page, generated from a template.
SocketHandler: Handles the websocket connection between the client page and 
                the server.
TextServer: The overall controller class which stores and controls 
            the model and visualization instance.

In theory, TextServer does NOT need to be subclassed on a model-by-model basis;
it should be able to create a browser visualization for any given standard.
TextVisualization subclass. 

A TextServer is created using two classes: one for the model, and one for the 
associated TextVisualization child class. The new TextServer can also accept 
arguments to pass to the first model instance. To go with the perennial Schelling
example, the following code 

    server = TextServer(SchellingModel, SchellingTextVisualization, "Schelling",
                            10, 10, 0.8, 0.2, 3)

creates a TextServer visualizing a SchellingModel via the 
SchellingTextVisualization, named "Schelling", with 10, 10... , 3 as the default
model parameters.

The server is launched using the launch() method. This runs the Tornado app, 
which consists of PageHandler and SocketHandler. At the moment, the server runs
the entire model (up to a default max_steps) prior to actually serving the data.
TODO: Make the model run a coroutine.
A dictionary associating each TextVisualization element's positional index and
visualization text is stored in a the TextServer's viz_state list, with position 
corresponding to the step it represents.

The client keeps track of what step it is showing. Clicking the Step button in
the browser sends a message requesting the viz_state corresponding to the next
step position, which is then sent back to the client via the websocket.

The websocket protocol is as follows: 
Each message is a JSON object, with a "type" property which defines the rest of
the structure.

Server -> Client

    {
    "type": "viz_state",
    "data": A JSON representation of the viz state text
    }

Client -> Server
    
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

import os

import tornado.ioloop
import tornado.template
import tornado.web
import tornado.websocket
import tornado.escape

class PageHandler(tornado.web.RequestHandler):
    def initialize(self, controller):
        self.controller = controller
        # TODO: This is a horrible hack and there's got to be a better way.
        path = os.path.dirname(__file__) + "/templates"
        loader = tornado.template.Loader(path)
        self.template = loader.load("text_template.html")

    def get(self):
        page = self.template.generate(
                    port = self.controller.port,
                    model_name=self.controller.model_name,
                    element_count = len(self.controller.visualization.elements))
        self.write(page)


class SocketHandler(tornado.websocket.WebSocketHandler):
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
            return_message = {"type": "viz_state"}
            return_message["data"] = self.controller.viz_states[step]
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



class TextServer(object):
    '''
    Main class for handling the visualization web app.

    Attributes:

    '''

    verbose = True

    model_name = "Mesa Model"
    model_cls = None # A model class
    text_visualization_cls = None # A visualization associated with that model
    port = 8888 # Port to listen on

    max_steps = 100
    viz_states = []

    model_args = ()
    model_kwargs = {}

    def __init__(self, model_cls, text_visualization_cls, name="Mesa Model",
                    *args, **kwargs):
        '''
        Create a new visualization server.

        Args:
            model_cls: A model class to visualize
            text_visualization_cls: The text visualization class associated with
                                    the model class.
            name: A name for the model.
            *args, **kwargs: Default arguments to create a model with. 
        '''
        self.model_name = name
        self.model_cls = model_cls
        self.text_visualization_cls = text_visualization_cls

        # TODO: Make this more elegant
        self.model_args = args
        self.model_kwargs = kwargs

        self.reset()

        self.application = tornado.web.Application([
            (r'/', PageHandler, {"controller": self}),
            (r'/ws', SocketHandler, {"controller": self})
            ])

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
        self.model = self.model_cls(*self.model_args, **self.model_kwargs)
        self.visualization = self.text_visualization_cls(self.model)
        self.viz_states = [self.get_viz()]

    def get_viz(self):
        '''
        Turn the current visualization state into a text dictionary.
        '''
        viz_state = {}
        for i, element in enumerate(self.visualization.elements):
            viz_state[i] = element.render()
        return viz_state

    def run_model(self):
        '''
        Run the model forward and store each viz state.
        #TODO: Have this run concurrently (I think) inside the event loop? 
        '''
        while self.model.schedule.steps < self.max_steps and self.model.running:
            self.model.step()
            self.viz_states.append(self.get_viz())
        print(self.model.schedule.steps)






        






