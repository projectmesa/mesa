import numpy as np
import solara
from matplotlib.figure import Figure

from mesa.examples.advanced.sugarscape_g1mt.model import SugarscapeG1mt
from mesa.visualization import Slider, SolaraViz, make_plot_component


def SpaceDrawer(model):
    def portray(g):
        layers = {
            "trader": {"x": [], "y": [], "c": "tab:red", "marker": "o", "s": 10},
        }

        for agent in g.all_cells.agents:
            i, j = agent.cell.coordinate
            layers["trader"]["x"].append(i)
            layers["trader"]["y"].append(j)
        return layers

    fig = Figure()
    ax = fig.subplots()
    out = portray(model.grid)
    # Sugar
    # Important note: imshow by default draws from upper left. You have to
    # always explicitly specify origin="lower".
    im = ax.imshow(
        np.ma.masked_where(model.grid.sugar.data <= 1, model.grid.sugar.data),
        cmap="spring",
        origin="lower",
    )
    fig.colorbar(im, orientation="vertical")
    # Spice
    ax.imshow(
        np.ma.masked_where(model.grid.spice.data <= 1, model.grid.spice.data),
        cmap="winter",
        origin="lower",
    )
    # Trader
    ax.scatter(**out["trader"])
    ax.set_axis_off()
    return solara.FigureMatplotlib(fig)


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "width": 50,
    "height": 50,
    # Population parameters
    "initial_population": Slider(
        "Initial Population", value=200, min=50, max=500, step=10
    ),
    # Agent endowment parameters
    "endowment_min": Slider("Min Initial Endowment", value=25, min=5, max=30, step=1),
    "endowment_max": Slider("Max Initial Endowment", value=50, min=30, max=100, step=1),
    # Metabolism parameters
    "metabolism_min": Slider("Min Metabolism", value=1, min=1, max=3, step=1),
    "metabolism_max": Slider("Max Metabolism", value=5, min=3, max=8, step=1),
    # Vision parameters
    "vision_min": Slider("Min Vision", value=1, min=1, max=3, step=1),
    "vision_max": Slider("Max Vision", value=5, min=3, max=8, step=1),
    # Trade parameter
    "enable_trade": {"type": "Checkbox", "value": True, "label": "Enable Trading"},
}

model = SugarscapeG1mt()

page = SolaraViz(
    model,
    components=[
        SpaceDrawer,
        make_plot_component("#Traders"),
        make_plot_component("Price"),
    ],
    model_params=model_params,
    name="Sugarscape {G1, M, T}",
    play_interval=150,
)
page  # noqa
