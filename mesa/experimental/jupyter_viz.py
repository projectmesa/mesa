import sys
import threading
from typing import List, Optional

import matplotlib.pyplot as plt
import networkx as nx
import reacton.ipywidgets as widgets
import solara
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from solara.alias import rv

import mesa

# Avoid interactive backend
plt.switch_backend("agg")


@solara.component
def JupyterViz(
    model_class,
    model_params,
    measures=None,
    name="Mesa Model",
    agent_portrayal=None,
    space_drawer="default",
    play_interval=150,
):
    """Initialize a component to visualize a model.
    Args:
        model_class: class of the model to instantiate
        model_params: parameters for initializing the model
        measures: list of callables or data attributes to plot
        name: name for display
        agent_portrayal: options for rendering agents (dictionary)
        space_drawer: method to render the agent space for
            the model; default implementation is the `SpaceMatplotlib` component;
            simulations with no space to visualize should
            specify `space_drawer=False`
        play_interval: play interval (default: 150)
    """
    current_step = solara.use_reactive(0)

    # 1. Set up model parameters
    user_params, fixed_params = split_model_params(model_params)
    model_parameters, set_model_parameters = solara.use_state(
        {**fixed_params, **{k: v["value"] for k, v in user_params.items()}}
    )

    # 2. Set up Model
    def make_model():
        model = model_class(**model_parameters)
        current_step.value = 0
        return model

    reset_counter = solara.use_reactive(0)
    model = solara.use_memo(
        make_model, dependencies=[*list(model_parameters.values()), reset_counter.value]
    )

    def handle_change_model_params(name: str, value: any):
        set_model_parameters({**model_parameters, name: value})

    def ColorCard(color, layout_type):
        # TODO: turn this into a Solara component, but must pass in current
        # step as a dependency for the plots, so that there is no flickering
        # due to rerender.
        with rv.Card(
            style_=f"background-color: {color}; width: 100%; height: 100%"
        ) as main:
            if "Space" in layout_type:
                rv.CardTitle(children=["Space"])
                if space_drawer == "default":
                    # draw with the default implementation
                    SpaceMatplotlib(
                        model, agent_portrayal, dependencies=[current_step.value]
                    )
                elif space_drawer:
                    # if specified, draw agent space with an alternate renderer
                    space_drawer(model, agent_portrayal)
            elif "Measure" in layout_type:
                rv.CardTitle(children=["Measure"])
                measure = measures[layout_type["Measure"]]
                if callable(measure):
                    # Is a custom object
                    measure(model)
                else:
                    make_plot(model, measure)
        return main

    # 3. Set up UI

    with solara.AppBar():
        solara.AppBarTitle(name)

    # render layout and plot

    # jupyter
    def render_in_jupyter():
        with solara.GridFixed(columns=2):
            UserInputs(user_params, on_change=handle_change_model_params)
            ModelController(model, play_interval, current_step, reset_counter)
            solara.Markdown(md_text=f"###Step - {current_step}")

        with solara.GridFixed(columns=2):
            # 4. Space
            if space_drawer == "default":
                # draw with the default implementation
                SpaceMatplotlib(
                    model, agent_portrayal, dependencies=[current_step.value]
                )
            elif space_drawer:
                # if specified, draw agent space with an alternate renderer
                space_drawer(model, agent_portrayal)
            # otherwise, do nothing (do not draw space)

            # 5. Plots

            for measure in measures:
                if callable(measure):
                    # Is a custom object
                    measure(model)
                else:
                    make_plot(model, measure)

    def render_in_browser():
        if measures:
            layout_types = [{"Space": "default"}] + [
                {"Measure": elem} for elem in range(len(measures))
            ]
        else:
            layout_types = [{"Space": "default"}]
        grid_layout_initial = get_initial_grid_layout(layout_types=layout_types)
        grid_layout, set_grid_layout = solara.use_state(grid_layout_initial)

        with solara.Sidebar():
            with solara.Card("Controls", margin=1, elevation=2):
                UserInputs(user_params, on_change=handle_change_model_params)
                ModelController(model, play_interval, current_step, reset_counter)
            with solara.Card("Progress", margin=1, elevation=2):
                solara.Markdown(md_text=f"####Step - {current_step}")

        items = [
            ColorCard(color="white", layout_type=layout_types[i])
            for i in range(len(layout_types))
        ]
        solara.GridDraggable(
            items=items,
            grid_layout=grid_layout,
            resizable=True,
            draggable=True,
            on_grid_layout=set_grid_layout,
        )

    if ("ipykernel" in sys.argv[0]) or ("colab_kernel_launcher.py" in sys.argv[0]):
        # When in Jupyter or Google Colab
        render_in_jupyter()
    else:
        render_in_browser()


@solara.component
def ModelController(model, play_interval, current_step, reset_counter):
    playing = solara.use_reactive(False)
    thread = solara.use_reactive(None)
    # We track the previous step to detect if user resets the model via
    # clicking the reset button or changing the parameters. If previous_step >
    # current_step, it means a model reset happens while the simulation is
    # still playing.
    previous_step = solara.use_reactive(0)

    def on_value_play(change):
        if previous_step.value > current_step.value and current_step.value == 0:
            # We add extra checks for current_step.value == 0, just to be sure.
            # We automatically stop the playing if a model is reset.
            playing.value = False
        elif model.running:
            do_step()
        else:
            playing.value = False

    def do_step():
        model.step()
        previous_step.value = current_step.value
        current_step.value = model.schedule.steps

    def do_play():
        model.running = True
        while model.running:
            do_step()

    def threaded_do_play():
        if thread is not None and thread.is_alive():
            return
        thread.value = threading.Thread(target=do_play)
        thread.start()

    def do_pause():
        if (thread is None) or (not thread.is_alive()):
            return
        model.running = False
        thread.join()

    def do_reset():
        reset_counter.value += 1

    def do_set_playing(value):
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
            height: 30px;
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
    model_params_input = {}
    model_params_fixed = {}
    for k, v in model_params.items():
        if check_param_is_fixed(v):
            model_params_fixed[k] = v
        else:
            model_params_input[k] = v
    return model_params_input, model_params_fixed


def check_param_is_fixed(param):
    if not isinstance(param, dict):
        return True
    if "type" not in param:
        return True


@solara.component
def UserInputs(user_params, on_change=None):
    """Initialize user inputs for configurable model parameters.
    Currently supports :class:`solara.SliderInt`, :class:`solara.SliderFloat`,
    :class:`solara.Select`, and :class:`solara.Checkbox`.

    Props:
        user_params: dictionary with options for the input, including label,
        min and max values, and other fields specific to the input type.
        on_change: function to be called with (name, value) when the value of an input changes.
    """

    for name, options in user_params.items():
        # label for the input is "label" from options or name
        label = options.get("label", name)
        input_type = options.get("type")

        def change_handler(value, name=name):
            on_change(name, value)

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


@solara.component
def SpaceMatplotlib(model, agent_portrayal, dependencies: Optional[List[any]] = None):
    space_fig = Figure()
    space_ax = space_fig.subplots()
    space = getattr(model, "grid", None)
    if space is None:
        # Sometimes the space is defined as model.space instead of model.grid
        space = model.space
    if isinstance(space, mesa.space.NetworkGrid):
        _draw_network_grid(space, space_ax, agent_portrayal)
    elif isinstance(space, mesa.space.ContinuousSpace):
        _draw_continuous_space(space, space_ax, agent_portrayal)
    else:
        _draw_grid(space, space_ax, agent_portrayal)
    space_ax.set_axis_off()
    solara.FigureMatplotlib(space_fig, format="png", dependencies=dependencies)


def _draw_grid(space, space_ax, agent_portrayal):
    def portray(g):
        x = []
        y = []
        s = []  # size
        c = []  # color
        for i in range(g.width):
            for j in range(g.height):
                content = g._grid[i][j]
                if not content:
                    continue
                if not hasattr(content, "__iter__"):
                    # Is a single grid
                    content = [content]
                for agent in content:
                    data = agent_portrayal(agent)
                    x.append(i)
                    y.append(j)
                    if "size" in data:
                        s.append(data["size"])
                    if "color" in data:
                        c.append(data["color"])
        out = {"x": x, "y": y}
        if len(s) > 0:
            out["s"] = s
        if len(c) > 0:
            out["c"] = c
        return out

    space_ax.scatter(**portray(space))


def _draw_network_grid(space, space_ax, agent_portrayal):
    graph = space.G
    pos = nx.spring_layout(graph, seed=0)
    nx.draw(
        graph,
        ax=space_ax,
        pos=pos,
        **agent_portrayal(graph),
    )


def _draw_continuous_space(space, space_ax, agent_portrayal):
    def portray(space):
        x = []
        y = []
        s = []  # size
        c = []  # color
        for agent in space._agent_to_index:
            data = agent_portrayal(agent)
            _x, _y = agent.pos
            x.append(_x)
            y.append(_y)
            if "size" in data:
                s.append(data["size"])
            if "color" in data:
                c.append(data["color"])
        out = {"x": x, "y": y}
        if len(s) > 0:
            out["s"] = s
        if len(c) > 0:
            out["c"] = c
        return out

    space_ax.scatter(**portray(space))


def make_plot(model, measure):
    fig = Figure()
    ax = fig.subplots()
    df = model.datacollector.get_model_vars_dataframe()
    ax.plot(df.loc[:, measure])
    ax.set_ylabel(measure)
    # Set integer x axis
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    solara.FigureMatplotlib(fig)


def make_text(renderer):
    def function(model):
        solara.Markdown(renderer(model))

    return function


def get_initial_grid_layout(layout_types):
    grid_lay = []
    y_coord = 0
    for ii in range(len(layout_types)):
        template_layout = {"h": 10, "i": 0, "moved": False, "w": 6, "y": 0, "x": 0}
        if ii == 0:
            grid_lay.append(template_layout)
        else:
            template_layout.update({"i": ii})
            if ii % 2 == 0:
                template_layout.update({"x": 0})
                y_coord += 16
            else:
                template_layout.update({"x": 6})
            template_layout.update({"y": y_coord})
            grid_lay.append(template_layout)
    return grid_lay
