import threading

import matplotlib.pyplot as plt
import reacton.ipywidgets as widgets
import solara
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

# Avoid interactive backend
plt.switch_backend("agg")


class JupyterContainer:
    def __init__(
        self,
        model_class,
        model_params,
        measures=None,
        name="Mesa Model",
        agent_portrayal=None,
    ):
        self.model_class = model_class
        self.split_model_params(model_params)
        self.measures = measures
        self.name = name
        self.agent_portrayal = agent_portrayal
        self.thread = None

    def split_model_params(self, model_params):
        self.model_params_input = {}
        self.model_params_fixed = {}
        for k, v in model_params.items():
            if self.check_param_is_fixed(v):
                self.model_params_fixed[k] = v
            else:
                self.model_params_input[k] = v

    def check_param_is_fixed(self, param):
        if not isinstance(param, dict):
            return True
        if "type" not in param:
            return True

    def do_step(self):
        self.model.step()
        self.set_df(self.model.datacollector.get_model_vars_dataframe())

    def do_play(self):
        self.model.running = True
        while self.model.running:
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

    def portray(self, g):
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
                    data = self.agent_portrayal(agent)
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


def make_space(viz):
    space_fig = Figure()
    space_ax = space_fig.subplots()
    space_ax.scatter(**viz.portray(viz.model.grid))
    space_ax.set_axis_off()
    solara.FigureMatplotlib(space_fig, dependencies=[viz.model, viz.df])


def make_plot(viz, measure):
    fig = Figure()
    ax = fig.subplots()
    ax.plot(viz.df.loc[:, measure])
    ax.set_ylabel(measure)
    # Set integer x axis
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    solara.FigureMatplotlib(fig, dependencies=[viz.model, viz.df])


def make_text(renderer):
    def function(viz):
        solara.Markdown(renderer(viz.model))

    return function


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


@solara.component
def MesaComponent(viz, space_drawer=None, play_interval=400):
    solara.Markdown(viz.name)

    # 1. User inputs
    user_inputs = {}
    for k, v in viz.model_params_input.items():
        user_input = solara.use_reactive(v["value"])
        user_inputs[k] = user_input.value
        make_user_input(user_input, k, v)

    # 2. Model
    def make_model():
        return viz.model_class(**user_inputs, **viz.model_params_fixed)

    viz.model = solara.use_memo(make_model, dependencies=list(user_inputs.values()))
    viz.df, viz.set_df = solara.use_state(
        viz.model.datacollector.get_model_vars_dataframe()
    )

    # 3. Buttons
    playing = solara.use_reactive(False)

    def on_value_play(change):
        if viz.model.running:
            viz.do_step()
        else:
            playing.value = False

    with solara.Row():
        solara.Button(label="Step", color="primary", on_click=viz.do_step)
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
        # threaded_do_play is not used for now because it
        # doesn't work in Google colab. We use
        # ipywidgets.Play until it is fixed. The threading
        # version is definite a much better implementation,
        # if it works.
        # solara.Button(label="▶", color="primary", on_click=viz.threaded_do_play)
        # solara.Button(label="⏸︎", color="primary", on_click=viz.do_pause)
        # solara.Button(label="Reset", color="primary", on_click=do_reset)

    with solara.GridFixed(columns=2):
        # 4. Space
        if space_drawer is None:
            make_space(viz)
        else:
            space_drawer(viz)
        # 5. Plots
        for measure in viz.measures:
            if callable(measure):
                # Is a custom object
                measure(viz)
            else:
                make_plot(viz, measure)


def JupyterViz(
    model_class,
    model_params,
    measures=None,
    name="Mesa Model",
    agent_portrayal=None,
    space_drawer=None,
    play_interval=400,
):
    return MesaComponent(
        JupyterContainer(model_class, model_params, measures, name, agent_portrayal),
        space_drawer=space_drawer,
        play_interval=play_interval,
    )
