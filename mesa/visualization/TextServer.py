'''
TextServer
==================================================

A simple experimental Tornado server which renders an arbitrary ASCII 
visualization in the browser.

Consists of the following classes:

PageHandler: The handler for the visualization page, generated from a template.
SocketHandler: Handles the websocket connection between 


'''

import tornado.ioloop
import tornado.template
import tornado.web
import tornado.websocket


class PageHandler(tornado.web.RequestHandler):
    def initialize(self, controller):
        self.controller = controller
        # TODO: This is a horrible hack and there's got to be a better way.
        path = "/Users/dmasad/Programming/ProjectMesa/mesa/mesa/visualization/templates"
        loader = tornado.template.Loader(path)
        self.template = loader.load("text_template.html")

    def get(self):
        page = self.template.generate(model_name=self.controller.model_name,
                    element_count = len(self.controller.visualization.elements))
        self.write(page)


class SocketHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, controller):
        self.controller = controller

    def open(self):
        print("Socket opened!")

    def on_message(self, message):
        '''
        Receiving a message from the websocket.
        '''
        print(message)
        if "get_step:" in message:
            step = int(message.split(":")[1])
            self.write_message(self.controller.viz_states[step])
        elif message == "RESET":
            self.controller.reset()
            self.write_message(self.controller.viz_states[0])
            self.controller.run_model()
        else:
            print("Unexpected message!")



class TextServer(object):
    '''
    Main class for handling the visualization web app.

    Attributes:

    '''

    model_name = "Mesa Model"
    model_cls = None # A model class
    text_visualization_cls = None # A visualization associated with that model
    port = 8888 # Port to listen on

    max_steps = 100
    viz_states = []

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

        self.reset(*args, **kwargs)

        self.application = tornado.web.Application([
            (r'/', PageHandler, {"controller": self}),
            (r'/ws', SocketHandler, {"controller": self})
            ])

    def launch(self, port=8888):
        '''
        Launch the server and have it listen on the given port.
        '''
        print("Launching server, listening on port", port)
        self.run_model()
        self.application.listen(port)
        tornado.ioloop.IOLoop.instance().start()

    def reset(self, *args, **kwargs):
        self.model = self.model_cls(*args, **kwargs)
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






        






