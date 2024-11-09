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

import threading

import reacton.ipywidgets as widgets
import solara
from solara.alias import rv

import mesa.experimental.components.altair as components_altair
import mesa.experimental.components.matplotlib as components_matplotlib
from mesa.experimental.UserParam import Slider


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
    model_class,
    model_params,
    measures=None,
    name=None,
    agent_portrayal=None,
    space_drawer="default",
    play_interval=150,
    seed=None,
):
    """Initialize a component to visualize a model.

    Args:
        model_class: Class of the model to instantiate
        model_params: Parameters for initializing the model
        measures: List of callables or data attributes to plot
        name: Name for display
        agent_portrayal: Options for rendering agents (dictionary);
            Default drawer supports custom `"size"`, `"color"`, and `"shape"`.
        space_drawer: Method to render the agent space for
            the model; default implementation is the `SpaceMatplotlib` component;
            simulations with no space to visualize should
            specify `space_drawer=False`
        play_interval: Play interval (default: 150)
        seed: The random seed used to initialize the model
    """
    if name is None:
        name = model_class.__name__

    current_step = solara.use_reactive(0)

    # 1. Set up model parameters
    reactive_seed = solara.use_reactive(0)
    user_params, fixed_params = split_model_params(model_params)
    model_parameters, set_model_parameters = solara.use_state(
        {**fixed_params, **{k: v.get("value") for k, v in user_params.items()}}
    )

    # 2. Set up Model
    def make_model():
        """Create a new model instance with current parameters and seed."""
        model = model_class.__new__(
            model_class, **model_parameters, seed=reactive_seed.value
        )
        model.__init__(**model_parameters)
        current_step.value = 0
        return model

    reset_counter = solara.use_reactive(0)
    model = solara.use_memo(
        make_model,
        dependencies=[
            *list(model_parameters.values()),
            reset_counter.value,
            reactive_seed.value,
        ],
    )

    def handle_change_model_params(name: str, value: any):
        """Update model parameters when user input changes."""
        set_model_parameters({**model_parameters, name: value})

    # 3. Set up UI

    with solara.AppBar():
        solara.AppBarTitle(name)

    # render layout and plot
    def do_reseed():
        """Update the random seed for the model."""
        reactive_seed.value = model.random.random()

    dependencies = [
        *list(model_parameters.values()),
        current_step.value,
        reactive_seed.value,
    ]

    # if space drawer is disabled, do not include it
    layout_types = [{"Space": "default"}] if space_drawer else []

    if measures:
        layout_types += [{"Measure": elem} for elem in range(len(measures))]

    grid_layout_initial = make_initial_grid_layout(layout_types=layout_types)
    grid_layout, set_grid_layout = solara.use_state(grid_layout_initial)

    with solara.Sidebar():
        with solara.Card("Controls", margin=1, elevation=2):
            solara.InputText(
                label="Seed",
                value=reactive_seed,
                continuous_update=True,
            )
            UserInputs(user_params, on_change=handle_change_model_params)
            ModelController(model, play_interval, current_step, reset_counter)
            solara.Button(label="Reseed", color="primary", on_click=do_reseed)
        with solara.Card("Information", margin=1, elevation=2):
            solara.Markdown(md_text=f"Step - {current_step}")

    items = [
        Card(
            model,
            measures,
            agent_portrayal,
            space_drawer,
            dependencies,
            color="white",
            layout_type=layout_types[i],
        )
        for i in range(len(layout_types))
    ]
    solara.GridDraggable(
        items=items,
        grid_layout=grid_layout,
        resizable=True,
        draggable=True,
        on_grid_layout=set_grid_layout,
    )


JupyterViz = SolaraViz


@solara.component
def ModelController(model, play_interval, current_step, reset_counter):
    """Create controls for model execution (step, play, pause, reset).

    Args:
        model: The model being visualized
        play_interval: Interval between steps during play
        current_step: Reactive value for the current step
        reset_counter: Counter to trigger model reset
    """
    playing = solara.use_reactive(False)
    thread = solara.use_reactive(None)
    # We track the previous step to detect if user resets the model via
    # clicking the reset button or changing the parameters. If previous_step >
    # current_step, it means a model reset happens while the simulation is
    # still playing.
    previous_step = solara.use_reactive(0)

    def on_value_play(change):
        """Handle play/pause state changes."""
        if previous_step.value > current_step.value and current_step.value == 0:
            # We add extra checks for current_step.value == 0, just to be sure.
            # We automatically stop the playing if a model is reset.
            playing.value = False
        elif model.running:
            do_step()
        else:
            playing.value = False

    def do_step():
        """Advance the model by one step."""
        model.step()
        previous_step.value = current_step.value
        current_step.value = model.steps

    def do_play():
        """Run the model continuously."""
        model.running = True
        while model.running:
            do_step()

    def threaded_do_play():
        """Start a new thread for continuous model execution."""
        if thread is not None and thread.is_alive():
            return
        thread.value = threading.Thread(target=do_play)
        thread.start()

    def do_pause():
        """Pause the model execution."""
        if (thread is None) or (not thread.is_alive()):
            return
        model.running = False
        thread.join()

    def do_reset():
        """Reset the model."""
        reset_counter.value += 1

    def do_set_playing(value):
        """Set the playing state."""
        if current_step.value == 0:
            # This means the model has been recreated, and the step resets to
            # 0. We want to avoid triggering the playing.value = False in the
            # on_value_play function.
            previous_step.value = current_step.value
        playing.set(value)

    with solara.Row():
        solara.Button(label="Step", color="primary", on_click=do_step)
        # This style is necessary so that the play widget has almost the same
        # height as typical Solara buttons.
        solara.Style(
            """
        .widget-play {
            height: 35px;
        }
        .widget-play button {
            color: white;
            background-color: #1976D2;  // Solara blue color
        }
        """
        )
        widgets.Play(
            value=0,
            interval=play_interval,
            repeat=True,
            show_repeat=False,
            on_value=on_value_play,
            playing=playing.value,
            on_playing=do_set_playing,
        )
        solara.Button(label="Reset", color="primary", on_click=do_reset)
        # threaded_do_play is not used for now because it
        # doesn't work in Google colab. We use
        # ipywidgets.Play until it is fixed. The threading
        # version is definite a much better implementation,
        # if it works.
        # solara.Button(label="▶", color="primary", on_click=viz.threaded_do_play)
        # solara.Button(label="⏸︎", color="primary", on_click=viz.do_pause)
        # solara.Button(label="Reset", color="primary", on_click=do_reset)


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
def UserInputs(user_params, on_change=None):
    """Initialize user inputs for configurable model parameters.

    Currently supports :class:`solara.SliderInt`, :class:`solara.SliderFloat`,
    :class:`solara.Select`, and :class:`solara.Checkbox`.

    Args:
        user_params: Dictionary with options for the input, including label,
        min and max values, and other fields specific to the input type.
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
