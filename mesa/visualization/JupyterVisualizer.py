import os
import threading
import time
import json
import ipywidgets as widgets
from IPython.display import (
    display,
    Javascript,
    HTML,
)
from mesa.visualization.UserParam import UserSettableParameter

MESA_VISUALIZER_ID_COUNT = 0


class JupyterVisualizer(object):
    """A helper for running Mesa visualizations inline in a notebook.

    The instantiation is similar to the ModularVisualization server but instead
    of starting the server the `display()` method should be called at the
    end of a notebook cell.

    ex:
    ```
        from mesa.visualization.ipython import (
            Visualizer,
        )
        from mesa.visualization.modules import (
            ChartModule,
        )

        chart = ChartModule(
            [{"Label": "Gini", "Color": "Black"}],
            data_collector_name='datacollector')
        v = Visualizer(MoneyModel, [chart], "Money Model", 100, 10, 10)
        v.display()
    ```
    """
    __name__ = "Execute Model Step"

    def __init__(self, model_cls, visualization_elements, name="Mesa Model",
                 model_params={}):
        global MESA_VISUALIZER_ID_COUNT
        self.identity = MESA_VISUALIZER_ID_COUNT
        MESA_VISUALIZER_ID_COUNT += 1

        display(Javascript("window.elements = [];"))
        display(Javascript("window.control = {};"))
        display(Javascript("window.control.tick = 0;"))

        # TODO: I've added a hardcoded div ID since the current visualization
        # implementations expect to inject into the body (I've hacked it in
        # the js files to always inject into this id).
        display(HTML("<div id='elements'></div>"))

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

        # Find the package includes path
        from mesa.visualization import ModularVisualization
        self.package_include_path = (
            os.path.dirname(ModularVisualization.__file__) +
            "/templates/js/")

        # Initializing the model
        self.model_name = name
        self.model_cls = model_cls
        self.description = 'No description available'
        if hasattr(model_cls, 'description'):
            self.description = model_cls.description
        elif model_cls.__doc__ is not None:
            self.description = model_cls.__doc__

        # Additions
        self.playing = False
        self.fps = 10

        self.model_kwargs = model_params
        self.reset_model()
    
    @property
    def user_params(self):
        result = {}
        for param, val in self.model_kwargs.items():
            if isinstance(val, UserSettableParameter):
                result[param] = val.json

        return result

    def reset_model(self, *args, **kwargs):
        """Reinstantiate the model object, using the current parameters."""
        model_params = {}
        for key, val in self.model_kwargs.items():
            if isinstance(val, UserSettableParameter):
                if val.param_type == 'static_text':    # static_text is never used for setting params
                    continue
                model_params[key] = val.value
            else:
                model_params[key] = val


        self.model = self.model_cls(**model_params)
        self.render_model()

        js = []

        for i, state in enumerate(self.visualization_elements):
            js.append("if(typeof(elements[{0}])!=='undefined') {{ elements[{1}].reset() }};".format(i, i)) #

        display(Javascript("window.control.tick = 0;"))
        display(Javascript("\n".join(js)))


    def render_model(self):
        """Turn the state of the model into a dictionary of visualizations."""
        visualization_state = []
        for element in self.visualization_elements:
            element_state = element.render(self.model)
            visualization_state.append(element_state)
        return visualization_state

    def step_model(self, *args, **kwargs):
        self.model.step()
        viz_states = self.render_model()
        js = []

        for i, state in enumerate(viz_states):
            js.append("elements[{0}].render({1});".format(
                i, json.dumps(state)))

        display(Javascript("window.control.tick += 1;"))
        display(Javascript("\n".join(js)))

    def work(self, *args, **kwargs):
        while self.playing:
            time.sleep(1. / self.fps)
            self.step_model(self, *args, **kwargs)

    def play_pause_model(self, *args, **kwargs):
        if self.playing == True:
            # self.thread.stop()
            self.playing = False
            self.button_play_pause.description = 'Play'
        else:
            self.playing = True
            self.thread = threading.Thread(target=self.work, args=(self, args, kwargs))
            self.thread.start()
            self.button_play_pause.description = 'Stop'


    def update_fps(self, change):
        self.fps = change.new


    def display(self, custom_js):
        """Display the visualization and controls"""
        self.button_play_pause = widgets.Button(description='Play')
        self.button_play_pause.on_click(self.play_pause_model)

        self.button_step = widgets.Button(description='Step The Model')
        self.button_step.on_click(self.step_model)

        self.button_reset = widgets.Button(description='Reset The Model')
        self.button_reset.on_click(self.reset_model)

        # Add FPS slider
        self.slider_fps = widgets.IntSlider(
            value=self.fps,
            min=1,
            max=20,
            step=1,
            description='Frames per second:',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        self.slider_fps.observe(self.update_fps, names='value')

        display(self.button_play_pause)
        display(self.button_step)
        display(self.button_reset)
        display(self.slider_fps)

        # Include the visualization js files
        for pi in self.package_includes:
            with open(self.package_include_path + pi) as f:
                js = f.read()
            display(HTML("<script>{0}</script>".format(js)))

        for li in self.local_includes:
            with open(li) as f:
                js = f.read()
            display(HTML("<script>{0}</script>".format(js)))

        js_all = "\n\t".join(self.js_code)
        rjs = custom_js.format(js_all)
        display(Javascript(rjs))
    