import matplotlib.pyplot as plt
import networkx as nx
import solara
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
import sys
from solara.alias import rv
from .model_control import ModelController
from .user_input import UserInputs
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
            the model; default implementation is :meth:`make_space`;
            simulations with no space to visualize should
            specify `space_drawer=False`
        play_interval: play interval (default: 150)
    """

    current_step, set_current_step = solara.use_state(0)

    # 1. Set up model parameters
    user_params, fixed_params = split_model_params(model_params)
    model_parameters, set_model_parameters = solara.use_state(
        {**fixed_params, **{k: v["value"] for k, v in user_params.items()}}
    )

    # 2. Set up Model
    def make_model():
        model = model_class(**model_parameters)
        set_current_step(0)
        return model

    reset_counter = solara.use_reactive(0)
    model = solara.use_memo(
        make_model, dependencies=[*list(model_parameters.values()), reset_counter.value]
    )

    def handle_change_model_params(name: str, value: any):
        set_model_parameters({**model_parameters, name: value})

    @solara.component
    def ColorCard(title, color, layout_type="Grid"):
        with rv.Card(
            style_=f"background-color: {color}; width: 100%; height: 100%"
        ) as main:
            rv.CardTitle(children=[title])
            if layout_type == "Grid":
                if space_drawer == "default":
                    # draw with the default implementation
                    make_space(model, agent_portrayal)
                elif space_drawer:
                    # if specified, draw agent space with an alternate renderer
                    space_drawer(model, agent_portrayal)
            elif layout_type == "Measure":
                for measure in measures:
                    if callable(measure):
                        # Is a custom object
                        measure(model)
                    else:
                        make_plot(model, measure)
        return main

    # 3. Set up UI

    with solara.AppBar():
        solara.AppBarTitle(name)

    grid_layout_initial = [
        {"h": 12, "i": "0", "moved": False, "w": 5, "x": 0, "y": 0},
        {"h": 12, "i": "1", "moved": False, "w": 5, "x": 7, "y": 0},
    ]

    colors = "white white".split()

    # we need to store the state of the grid_layout ourselves, otherwise it will 'reset'
    # each time we change resizable or draggable
    grid_layout, set_grid_layout = solara.use_state(grid_layout_initial)

    # render layout and plot

    # jupyter
    def render_in_jupyter():
        with solara.Row():
            with solara.Card("Controls", margin=1, elevation=2):
                UserInputs(user_params, on_change=handle_change_model_params)
                ModelController(
                    model, play_interval, current_step, set_current_step, reset_counter
                )
            with solara.Card("Progress", margin=1, elevation=2):
                # solara.ProgressLinear(True)
                solara.Markdown(md_text=f"####Step - {current_step}")

        with solara.Row():
            # 4. Space
            if space_drawer == "default":
                # draw with the default implementation
                make_space(model, agent_portrayal)
            elif space_drawer:
                # if specified, draw agent space with an alternate renderer
                space_drawer(model, agent_portrayal)
            # otherwise, do nothing (do not draw space)

        # 5. Plots
        with solara.GridFixed(columns=len(measures)):
            for measure in measures:
                if callable(measure):
                    # Is a custom object
                    measure(model)
                else:
                    make_plot(model, measure)

    def render_in_browser():
        with solara.Sidebar():
            with solara.Card("Controls", margin=1, elevation=2):
                UserInputs(user_params, on_change=handle_change_model_params)
                ModelController(
                    model, play_interval, current_step, set_current_step, reset_counter
                )
            with solara.Card("Progress", margin=1, elevation=2):
                # solara.ProgressLinear(True)
                solara.Markdown(md_text=f"####Step - {current_step}")
            resizable = solara.ui_checkbox("Allow resizing", value=True)
            draggable = solara.ui_checkbox("Allow dragging", value=True)

        layout_types = ["Grid", "Measure"]

        items = [
            ColorCard(
                title=layout_types[i], color=colors[i], layout_type=layout_types[i]
            )
            for i in range(len(grid_layout))
        ]
        solara.GridDraggable(
            items=items,
            grid_layout=grid_layout,
            resizable=resizable,
            draggable=draggable,
            on_grid_layout=set_grid_layout,
        )

    if "ipykernel" in sys.argv[0]:
        render_in_jupyter()
    else:
        render_in_browser()


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


def make_space(model, agent_portrayal):
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
    solara.FigureMatplotlib(space_fig, format="png")


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
