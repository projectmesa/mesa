'''
Modular Visualization for Mesa

The idea of a modular visualization is as follows: 

'''

import os

import tornado.ioloop
import tornado.template
import tornado.web
import tornado.websocket
import tornado.escape

# Suppress several pylint warnings for this file.
# Attributes being defined outside of init is a Tornado feature.
# pylint: disable=attribute-defined-outside-init


class VisualizationElement(object):
    '''
    Defines an element of the visualization.

    Attributes:
        template: HTML template for the visualization.
        render_js: JavaScript code to render the data.

    Methods:
        render: Takes a model object, and produces JSON data which can be sent
                to the client.
    '''

    template = None
    render_args = {}

    def __init__(self):
        pass

    def render(self, model):
        '''
        Build visualization data from a model object.

        Args:
            model: A model object

        Returns:
            A JSON-ready object.
        '''
        return "<b>VisualizationElement goes here."

# =============================================================================

class VisualizationModule(tornado.web.UIModule):
    '''
    Basic visualization module. Takes a VisualizationElement subclass at 
    render-time, and uses its properties to render.
    '''

    def render(self, element):
        return self.render_string(element.template, index=element.index, 
                                  **element.render_args) 

class PageHandler(tornado.web.RequestHandler):
    '''
    Handler for the HTML template which holds the visualization.
    '''
    def initialize(self):
        path = os.path.dirname(__file__) + "/templates"

    def get(self):
        elements = self.application.visualization_elements
        for i, element in enumerate(elements):
            element.index = i
        self.render("modular_template.html", port=self.application.port, 
                    model_name=self.application.model_name, elements=elements)

class SocketHandler(tornado.websocket.WebSocketHandler):
    '''
    Handler for websocket.
    '''

    def open(self):
        if self.application.verbose:
            print("Socket opened!")

    def on_message(self, message):
        '''
        Receiving a message from the websocket, parse, and act accordingly.
        '''
        if self.application.verbose:
            print(message)
        msg = tornado.escape.json_decode(message)

        if msg["type"] == "get_step":
            step = int(msg["step"])
            if step < len(self.application.viz_states):
                return_message = {"type": "viz_state"}
                return_message["data"] = self.application.viz_states[step]
            else:
                return_message = {"type": "end"}
            self.write_message(return_message)

        elif msg["type"] == "reset":
            self.application.reset_model()
            return_message = {"type": "viz_state"}
            return_message["data"] = self.application.viz_states[0]

            self.write_message(return_message)
            self.application.run_model()

        else:
            if self.application.verbose:
                print("Unexpected message!")


class ModularServer(tornado.web.Application):
    '''
    Main visualization application.
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

    def __init__(self, model_cls, visualization_elements, name="Mesa Model", 
                 *args, **kwargs):
        '''
        Create a new visualization server with the given elements.
        '''
        self.visualization_elements = visualization_elements

        # Initializing the model
        self.model_name = name
        self.model_cls = model_cls

        self.model_args = args
        self.model_kwargs = kwargs
        self.reset_model()

        # Initializing the application itself:
        page_handler = (r'/', PageHandler)
        socket_handler = (r'/ws', SocketHandler)
        settings = {"ui_modules": {"VisualizationModule": VisualizationModule},
                    "template_path": os.path.dirname(__file__) + "/templates",
                    "static_path": os.path.dirname(__file__) + "/templates"}
        super().__init__([page_handler, socket_handler], **settings)

    def reset_model(self):
        '''
        Reinstantiate the model object, using the current parameters.
        '''
        self.model = self.model_cls(*self.model_args, **self.model_kwargs)
        self.viz_states = [self.render_model()]

    def render_model(self):
        '''
        Turn the current state of the model into a dictionary of visualizations
        '''
        visualization_state = []
        for element in self.visualization_elements:
            element_state = element.render(self.model)
            visualization_state.append(element_state)
        return visualization_state  

    def run_model(self):
        '''
        Run the model forward and store each viz state.
        #TODO: Have this run concurrently (I think) inside the event loop?
        '''
        while self.model.schedule.steps < self.max_steps and self.model.running:
            self.model.step()
            self.viz_states.append(self.render_model())
        if self.verbose:
            print("Model steps:", self.model.schedule.steps)







