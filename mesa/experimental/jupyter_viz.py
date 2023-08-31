import threading

import networkx as nx
import reacton.ipywidgets as widgets
import solara
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

import mesa


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
    for k, v in model_params_input.items():
        user_input = solara.use_reactive(v["value"])
        user_inputs[k] = user_input.value
        make_user_input(user_input, k, v)

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
                make_plot(model, measure)


@solara.component
def ModelController(model, play_interval, current_step, set_current_step):
    playing = solara.use_reactive(False)

    def on_value_play(change):
        if model.running:
            do_step()
        else:
            playing.value = False

    def do_step():
        model.step()
        set_current_step(model.schedule.steps)

    def do_play(self):
        model.running = True
        while model.running:
            self.do_step()

    def threaded_do_play(self):
        if self.thread is not None and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self.do_play)
        self.thread.start()

    def do_pause(self):
        if (self.thread is None) or (not self.thread.is_alive()):
            return
        self.model.running = False
        self.thread.join()

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
            on_playing=playing.set,
        )
        solara.Markdown(md_text=f"**Step:** {current_step}")
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


def make_user_input(user_input, k, v):
    if v["type"] == "SliderInt":
        solara.SliderInt(
            v.get("label", "label"),
            value=user_input,
            min=v.get("min"),
            max=v.get("max"),
            step=v.get("step"),
        )
    elif v["type"] == "SliderFloat":
        solara.SliderFloat(
            v.get("label", "label"),
            value=user_input,
            min=v.get("min"),
            max=v.get("max"),
            step=v.get("step"),
        )
    elif v["type"] == "Select":
        solara.Select(
            v.get("label", "label"),
            value=v.get("value"),
            values=v.get("values"),
        )


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
