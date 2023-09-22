import copy

import matplotlib.pyplot as plt
import networkx as nx
import reacton.ipywidgets as widgets
import solara
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

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
    play_interval=400,
    timeline=False,
):
    """Initialize a component to visualize a model.
    Args:
        model_class: class of the model to instantiate
        model_params: parameters for initializing the model
        measures: list of callables or data attributes to plot
        name: name for display
        agent_portrayal: options for rendering agents (dictionary)
        space_drawer: method to render the agent space for
            the model; default implementation is :meth:`make_space`;
            simulations with no space to visualize should
            specify `space_drawer=False`
        play_interval: play interval (default: 400)
        timeline: whether to display a scrubbable timeline (default: False)
    """

    # 1. Set up model parameters
    user_params, fixed_params = split_model_params(model_params)
    model_parameters, set_model_parameters = solara.use_state(
        {**fixed_params, **{k: v["value"] for k, v in user_params.items()}}
    )

    model, set_model = solara.use_state(model_class(**model_parameters))
    model_cache, set_model_cache = solara.use_state({0: model})

    # 2. Set up Model
    def make_model():
        model = model_class(**model_parameters)
        set_model(model)
        set_model_cache({0: model})

    solara.use_memo(
        make_model,
        dependencies=list(model_parameters.values()),
    )

    def handle_change_model_params(name: str, value: any):
        set_model_parameters({**model_parameters, name: value})

    def do_step():
        if not model.running:
            return

        updated_model = copy.deepcopy(model)
        updated_model.step()
        set_model(updated_model)

    def handle_step_timeline(step: int):
        if step == model.schedule.steps:
            return

        set_model_cache({**model_cache, model.schedule.steps: model})

        if step in model_cache:
            previous_model = model_cache[step]
            set_model(previous_model)
        else:
            do_step()

    # 3. Set up UI
    solara.Markdown(name)
    UserInputs(user_params, on_change=handle_change_model_params)
    TimelineControls(
        play_interval=play_interval,
        on_step=handle_step_timeline,
        on_reset=make_model,
        current_step=model.schedule.steps,
        max_step=max(*model_cache.keys(), model.schedule.steps),
    ) if timeline else BaseControls(
        play_interval=play_interval,
        on_step=do_step,
        on_reset=make_model,
    )

    with solara.GridFixed(columns=2):
        # 4. Space
        if space_drawer == "default":
            # draw with the default implementation
            make_space(model, agent_portrayal)
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


@solara.component
def BaseControls(play_interval, on_step, on_reset):
    playing = solara.use_reactive(False)

    def on_value_play(_):
        if playing.value:
            on_step()

    def reset():
        playing.value = False
        on_reset()

    with solara.Card(), solara.Row(gap="2px", style={"align-items": "center"}):
        with solara.Tooltip("Reset the model"):
            solara.Button(icon_name="mdi-reload", color="primary", on_click=reset)

        with solara.Tooltip("Step forward"):
            solara.Button(label="+1", color="primary", on_click=on_step)

        with solara.Tooltip("Start/Stop the model"):
            widgets.Play(
                interval=play_interval,
                show_repeat=False,
                on_value=on_value_play,
                playing=playing.value,
                on_playing=playing.set,
                layout=widgets.Layout(height="36px"),
            )


@solara.component
def TimelineControls(play_interval, on_step, on_reset, current_step, max_step):
    playing = solara.use_reactive(False)

    def on_value_play(_):
        if playing.value:
            on_step(current_step + 1)

    def change_step(value):
        return lambda: on_step(max(0, value))

    def reset():
        playing.value = False
        on_reset()

    with solara.Card(), solara.Column(
        gap="40px",
    ):
        with solara.Row(gap="2px", style={"align-items": "center"}):
            with solara.Tooltip("Reset the model"):
                solara.Button(icon_name="mdi-reload", color="primary", on_click=reset)
            with solara.Tooltip("Step backward to the beginning"):
                solara.Button(
                    icon_name="mdi-skip-backward",
                    color="primary",
                    on_click=change_step(0),
                )
            with solara.Tooltip("Step backward"):
                solara.Button(
                    label="-1",
                    color="primary",
                    on_click=change_step(current_step - 1),
                )
            with solara.Tooltip("Start/Stop the model"):
                widgets.Play(
                    interval=play_interval,
                    show_repeat=False,
                    on_value=on_value_play,
                    playing=playing.value,
                    on_playing=playing.set,
                    layout=widgets.Layout(height="36px"),
                )
            with solara.Tooltip("Step forward"):
                solara.Button(
                    label="+1",
                    color="primary",
                    on_click=change_step(current_step + 1),
                )
            with solara.Tooltip("Step forward to the end"):
                solara.Button(
                    icon_name="mdi-skip-forward",
                    color="primary",
                    on_click=change_step(max_step),
                )
        solara.SliderInt(
            label="Timeline (current step)",
            value=current_step,
            min=0,
            max=max_step,
            thumb_label="always",
            step=1,
            on_value=on_step,
        )


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
                value=options.get("value"),
            )
        else:
            raise ValueError(f"{input_type} is not a supported input type")


def make_space(model, agent_portrayal):
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

    space_fig = Figure()
    space_ax = space_fig.subplots()
    if isinstance(model.grid, mesa.space.NetworkGrid):
        _draw_network_grid(model, space_ax, agent_portrayal)
    else:
        space_ax.scatter(**portray(model.grid))
    space_ax.set_axis_off()
    solara.FigureMatplotlib(space_fig)


def _draw_network_grid(model, space_ax, agent_portrayal):
    graph = model.grid.G
    pos = nx.spring_layout(graph, seed=0)
    nx.draw(
        graph,
        ax=space_ax,
        pos=pos,
        **agent_portrayal(graph),
    )


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
