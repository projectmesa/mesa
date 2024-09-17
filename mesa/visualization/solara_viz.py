"""Mesa visualization module for creating interactive model visualizations.

This module provides components to create browser- and Jupyter notebook-based visualizations of
Mesa models, allowing users to watch models run step-by-step and interact with model parameters.

Key features:
    - SolaraViz: Main component for creating visualizations, supporting grid displays and plots
    - ModelController: Handles model execution controls (step, play, pause, reset)
    - UserInputs: Generates UI elements for adjusting model parameters
    - Card: Renders individual visualization elements (space, measures)

The module uses Solara for rendering in Jupyter notebooks or as standalone web applications.
It supports various types of visualizations including matplotlib plots, agent grids, and
custom visualization components.

Usage:
    1. Define an agent_portrayal function to specify how agents should be displayed
    2. Set up model_params to define adjustable parameters
    3. Create a SolaraViz instance with your model, parameters, and desired measures
    4. Display the visualization in a Jupyter notebook or run as a Solara app

See the Visualization Tutorial and example models for more details.
"""

import copy
import time
from typing import TYPE_CHECKING, Literal

import solara
from solara.alias import rv

import mesa.visualization.components.altair as components_altair
import mesa.visualization.components.matplotlib as components_matplotlib
from mesa.visualization.UserParam import Slider
from mesa.visualization.utils import force_update, update_counter

if TYPE_CHECKING:
    from mesa.model import Model


# TODO: Turn this function into a Solara component once the current_step.value
# dependency is passed to measure()
def Card(
    model, measures, agent_portrayal, space_drawer, dependencies, color, layout_type
):
    """Create a card component for visualizing model space or measures.

    Args:
        model: The Mesa model instance
        measures: List of measures to be plotted
        agent_portrayal: Function to define agent appearance
        space_drawer: Method to render agent space
        dependencies: List of dependencies for updating the visualization
        color: Background color of the card
        layout_type: Type of layout (Space or Measure)

    Returns:
        rv.Card: A card component containing the visualization
    """
    with rv.Card(
        style_=f"background-color: {color}; width: 100%; height: 100%"
    ) as main:
        if "Space" in layout_type:
            rv.CardTitle(children=["Space"])
            if space_drawer == "default":
                # draw with the default implementation
                components_matplotlib.SpaceMatplotlib(
                    model, agent_portrayal, dependencies=dependencies
                )
            elif space_drawer == "altair":
                components_altair.SpaceAltair(
                    model, agent_portrayal, dependencies=dependencies
                )
            elif space_drawer:
                # if specified, draw agent space with an alternate renderer
                space_drawer(model, agent_portrayal, dependencies=dependencies)
        elif "Measure" in layout_type:
            rv.CardTitle(children=["Measure"])
            measure = measures[layout_type["Measure"]]
            if callable(measure):
                # Is a custom object
                measure(model)
            else:
                components_matplotlib.PlotMatplotlib(
                    model, measure, dependencies=dependencies
                )
    return main


@solara.component
def SolaraViz(
    model: "Model" | solara.Reactive["Model"],
    components: list[solara.component] | Literal["default"] = "default",
    play_interval=100,
    model_params=None,
    seed=0,
    name: str | None = None,
):
    """Solara visualization component.

    Args:
        model: a Model instance
        components: list of solara components
        play_interval: int
        model_params: parameters for instantiating a model
        seed: the seed for the rng
        name: str

    """
    update_counter.get()
    if components == "default":
        components = [components_altair.make_space_altair()]

    # Convert model to reactive
    if not isinstance(model, solara.Reactive):
        model = solara.use_reactive(model)

    def connect_to_model():
        # Patch the step function to force updates
        original_step = model.value.step

        def step():
            original_step()
            force_update()

        model.value.step = step
        # Add a trigger to model itself
        model.value.force_update = force_update
        force_update()

    solara.use_effect(connect_to_model, [model.value])

    with solara.AppBar():
        solara.AppBarTitle(name if name else model.value.__class__.__name__)

    with solara.Sidebar():
        with solara.Card("Controls", margin=1, elevation=2):
            if model_params is not None:
                ModelCreator(
                    model,
                    model_params,
                    seed=seed,
                )
            ModelController(model, play_interval)
        with solara.Card("Information", margin=1, elevation=2):
            ShowSteps(model.value)

    solara.Column(
        [
            *(component(model.value) for component in components),
        ]
    )


JupyterViz = SolaraViz


@solara.component
def ModelController(model: solara.Reactive["Model"], play_interval=100):
    """Create controls for model execution (step, play, pause, reset).

    Args:
        model: The reactive model being visualized
        play_interval: Interval between steps during play
    """
    if not isinstance(model, solara.Reactive):
        model = solara.use_reactive(model)

    playing = solara.use_reactive(False)
    original_model = solara.use_reactive(None)

    def save_initial_model():
        """Save the initial model for comparison."""
        original_model.set(copy.deepcopy(model.value))
        playing.value = False
        force_update()

    solara.use_effect(save_initial_model, [model.value])

    def step():
        while playing.value:
            time.sleep(play_interval / 1000)
            do_step()

    solara.use_thread(step, [playing.value])

    def do_step():
        """Advance the model by one step."""
        model.value.step()

    def do_play():
        """Run the model continuously."""
        playing.value = True

    def do_pause():
        """Pause the model execution."""
        playing.value = False

    def do_reset():
        """Reset the model to its initial state."""
        playing.value = False
        model.value = copy.deepcopy(original_model.value)

    with solara.Row(justify="space-between"):
        solara.Button(label="Reset", color="primary", on_click=do_reset)
        solara.Button(label="Step", color="primary", on_click=do_step)
        solara.Button(label="▶", color="primary", on_click=do_play)
        solara.Button(label="⏸︎", color="primary", on_click=do_pause)


def split_model_params(model_params):
    """Split model parameters into user-adjustable and fixed parameters.

    Args:
        model_params: Dictionary of all model parameters

    Returns:
        tuple: (user_adjustable_params, fixed_params)
    """
    model_params_input = {}
    model_params_fixed = {}
    for k, v in model_params.items():
        if check_param_is_fixed(v):
            model_params_fixed[k] = v
        else:
            model_params_input[k] = v
    return model_params_input, model_params_fixed


def check_param_is_fixed(param):
    """Check if a parameter is fixed (not user-adjustable).

    Args:
        param: Parameter to check

    Returns:
        bool: True if parameter is fixed, False otherwise
    """
    if isinstance(param, Slider):
        return False
    if not isinstance(param, dict):
        return True
    if "type" not in param:
        return True


@solara.component
def ModelCreator(model, model_params, seed=1):
    """Helper class to create a new Model instance.

    Args:
        model: model instance
        model_params: model parameters
        seed: the seed to use for the random number generator


    """
    user_params, fixed_params = split_model_params(model_params)

    reactive_seed = solara.use_reactive(seed)

    model_parameters, set_model_parameters = solara.use_state(
        {
            **fixed_params,
            **{k: v.get("value") for k, v in user_params.items()},
        }
    )

    def do_reseed():
        """Update the random seed for the model."""
        reactive_seed.value = model.value.random.random()

    def on_change(name, value):
        set_model_parameters({**model_parameters, name: value})

    def create_model():
        model.value = model.value.__class__(**model_parameters)
        model.value._seed = reactive_seed.value

    solara.use_effect(create_model, [model_parameters, reactive_seed.value])

    solara.InputText(
        label="Seed",
        value=reactive_seed,
        continuous_update=True,
    )

    solara.Button(label="Reseed", color="primary", on_click=do_reseed)

    UserInputs(user_params, on_change=on_change)


@solara.component
def UserInputs(user_params, on_change=None):
    """Initialize user inputs for configurable model parameters.

    Currently supports :class:`solara.SliderInt`, :class:`solara.SliderFloat`,
    :class:`solara.Select`, and :class:`solara.Checkbox`.

    Args:
        user_params: Dictionary with options for the input, including label, min and max values, and other fields specific to the input type.
        on_change: Function to be called with (name, value) when the value of an input changes.
    """
    for name, options in user_params.items():

        def change_handler(value, name=name):
            on_change(name, value)

        if isinstance(options, Slider):
            slider_class = (
                solara.SliderFloat if options.is_float_slider else solara.SliderInt
            )
            slider_class(
                options.label,
                value=options.value,
                on_value=change_handler,
                min=options.min,
                max=options.max,
                step=options.step,
            )
            continue

        # label for the input is "label" from options or name
        label = options.get("label", name)
        input_type = options.get("type")
        if input_type == "SliderInt":
            solara.SliderInt(
                label,
                value=options.get("value"),
                on_value=change_handler,
                min=options.get("min"),
                max=options.get("max"),
                step=options.get("step"),
            )
        elif input_type == "SliderFloat":
            solara.SliderFloat(
                label,
                value=options.get("value"),
                on_value=change_handler,
                min=options.get("min"),
                max=options.get("max"),
                step=options.get("step"),
            )
        elif input_type == "Select":
            solara.Select(
                label,
                value=options.get("value"),
                on_value=change_handler,
                values=options.get("values"),
            )
        elif input_type == "Checkbox":
            solara.Checkbox(
                label=label,
                on_value=change_handler,
                value=options.get("value"),
            )
        else:
            raise ValueError(f"{input_type} is not a supported input type")


def make_text(renderer):
    """Create a function that renders text using Markdown.

    Args:
        renderer: Function that takes a model and returns a string

    Returns:
        function: A function that renders the text as Markdown
    """

    def function(model):
        solara.Markdown(renderer(model))

    return function


def make_initial_grid_layout(layout_types):
    """Create an initial grid layout for visualization components.

    Args:
        layout_types: List of layout types (Space or Measure)

    Returns:
        list: Initial grid layout configuration
    """
    return [
        {
            "i": i,
            "w": 6,
            "h": 10,
            "moved": False,
            "x": 6 * (i % 2),
            "y": 16 * (i - i % 2),
        }
        for i in range(len(layout_types))
    ]


@solara.component
def ShowSteps(model):  # noqa D103
    update_counter.get()
    return solara.Text(f"Step: {model.steps}")
