import time

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
    space_drawer=None,
    play_interval=400,
):
    current_step, set_current_step = solara.use_state(0)

    solara.Markdown(name)

    # 0. Split model params
    model_params_input, model_params_fixed = split_model_params(model_params)

    # 1. User inputs
    user_inputs = {}
    for name, options in model_params_input.items():
        user_input = solara.use_reactive(options["value"])
        user_inputs[name] = user_input.value
        make_user_input(user_input, name, options)

    # 2. Model
    def make_model():
        return model_class(**user_inputs, **model_params_fixed)

    model = solara.use_memo(make_model, dependencies=list(user_inputs.values()))

    # 3. Buttons
    ModelController(model, play_interval, current_step, set_current_step)

    with solara.GridFixed(columns=2):
        # 4. Space
        if space_drawer is None:
            make_space(model, agent_portrayal)
        else:
            space_drawer(model, agent_portrayal)
        # 5. Plots
        for measure in measures:
            if callable(measure):
                # Is a custom object
                measure(model)
            else:
                pass
                # make_plot(model, measure)


@solara.component
def ModelController(model, play_interval, current_step, set_current_step):
    playing = solara.use_reactive(False)

    def do_step():
        model.step()
        set_current_step(model.schedule.steps)

    def do_play():
        if playing.value and model.running:
            do_step()
            time.sleep(play_interval)

    solara.use_thread(
        do_play, dependencies=[playing.value, model.running, current_step]
    )

    def handle_click_start_pause():
        playing.value = not playing.value

    def handle_click_step():
        do_step()

    with solara.Row():
        solara.Button(
            label="Start" if not playing.value else "Pause",
            color="primary",
            on_click=handle_click_start_pause,
        )
        solara.Button(
            label="Step",
            color="primary",
            on_click=handle_click_step,
            disabled=playing.value,
        )
        # solara.Button(label="Reset", color="primary", on_click=do_reset)
        solara.Markdown(md_text=f"**Step:** {current_step}")


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


def make_user_input(user_input, name, options):
    """Initialize a user input for configurable model parameters.
    Currently supports :class:`solara.SliderInt`, :class:`solara.SliderFloat`,
    and :class:`solara.Select`.

    Args:
        user_input: :class:`solara.reactive` object with initial value
        name: field name; used as fallback for label if 'label' is not in options
        options: dictionary with options for the input, including label,
        min and max values, and other fields specific to the input type.
    """
    # label for the input is "label" from options or name
    label = options.get("label", name)
    input_type = options.get("type")
    if input_type == "SliderInt":
        solara.SliderInt(
            label,
            value=user_input,
            min=options.get("min"),
            max=options.get("max"),
            step=options.get("step"),
        )
    elif input_type == "SliderFloat":
        solara.SliderFloat(
            label,
            value=user_input,
            min=options.get("min"),
            max=options.get("max"),
            step=options.get("step"),
        )
    elif input_type == "Select":
        solara.Select(
            label,
            value=options.get("value"),
            values=options.get("values"),
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
