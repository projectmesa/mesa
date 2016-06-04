import os
import json
import ipywidgets as widgets
from IPython.display import (
    display,
    Javascript,
    HTML,
)
MESA_VISUALIZER_ID_COUNT = 0


class Visualizer(object):
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
                 *args, **kwargs):
        global MESA_VISUALIZER_ID_COUNT
        self.identity = MESA_VISUALIZER_ID_COUNT
        MESA_VISUALIZER_ID_COUNT += 1

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
            "/templates/")

        # Initializing the model
        self.model_name = name
        self.model_cls = model_cls

        self.model_args = args
        self.model_kwargs = kwargs
        self.reset_model()

    def reset_model(self, *args, **kwargs):
        """Reinstantiate the model object, using the current parameters."""
        self.model = self.model_cls(*self.model_args, **self.model_kwargs)
        self.render_model()

        js = []

        for i, state in enumerate(self.visualization_elements):
            js.append("elements[{0}].reset();".format(i))

        display(Javascript("window.control.tick = 0;"))
        display(Javascript("\n".join(js)))

    def render_model(self, *args, **kwargs):
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

    def display(self):
        """Display the visualization and controls"""
        self.button_step = widgets.Button(description='Step The Model')
        self.button_step.on_click(self.step_model)

        self.button_reset = widgets.Button(description='Reset The Model')
        self.button_reset.on_click(self.reset_model)

        display(self.button_step)
        display(self.button_reset)

        display(Javascript("window.elements = [];"))
        display(Javascript("window.control = {};"))
        display(Javascript("window.control.tick = 0;"))

        # Include the visualization js files
        for pi in self.package_includes:
            with open(self.package_include_path + pi) as f:
                js = f.read()

            display(HTML("<script>{0}</script>".format(js)))

        for li in self.local_includes:
            with open(li) as f:
                js = f.read()

            display(HTML("<script>{0}</script>".format(js)))

        # TODO: I've added a hardcoded div ID since the current visualization
        # implementations expect to inject into the body (I've hacked it in
        # the js files to always inject into this id).
        display(HTML("<div id='my-div-tag-to-store-chart'></div>"))

        # Run the initialization script for each visualization
        for js in self.js_code:
            display(Javascript(js))
