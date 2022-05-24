import mesa

from charts.agents import Person
from charts.model import Charts

"""
Citation:
The following code was adapted from server.py at
https://github.com/projectmesa/mesa/blob/main/examples/wolf_sheep/wolf_sheep/server.py
Accessed on: November 2, 2017
Author of original code: Taylor Mutch
"""

# The colors here are taken from Matplotlib's tab10 palette
# Green
RICH_COLOR = "#2ca02c"
# Red
POOR_COLOR = "#d62728"
# Blue
MID_COLOR = "#1f77b4"


def person_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    # update portrayal characteristics for each Person object
    if isinstance(agent, Person):
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
        portrayal["Layer"] = 0
        portrayal["Filled"] = "true"

        color = MID_COLOR

        # set agent color based on savings and loans
        if agent.savings > agent.model.rich_threshold:
            color = RICH_COLOR
        if agent.savings < 10 and agent.loans < 10:
            color = MID_COLOR
        if agent.loans > 10:
            color = POOR_COLOR

        portrayal["Color"] = color

    return portrayal


# dictionary of user settable parameters - these map to the model __init__ parameters
model_params = {
    "init_people": mesa.visualization.Slider(
        "People", 25, 1, 200, description="Initial Number of People"
    ),
    "rich_threshold": mesa.visualization.Slider(
        "Rich Threshold",
        10,
        1,
        20,
        description="Upper End of Random Initial Wallet Amount",
    ),
    "reserve_percent": mesa.visualization.Slider(
        "Reserves",
        50,
        1,
        100,
        description="Percent of deposits the bank has to hold in reserve",
    ),
}

# set the portrayal function and size of the canvas for visualization
canvas_element = mesa.visualization.CanvasGrid(person_portrayal, 20, 20, 500, 500)

# map data to chart in the ChartModule
line_chart = mesa.visualization.ChartModule(
    [
        {"Label": "Rich", "Color": RICH_COLOR},
        {"Label": "Poor", "Color": POOR_COLOR},
        {"Label": "Middle Class", "Color": MID_COLOR},
    ]
)

model_bar = mesa.visualization.BarChartModule(
    [
        {"Label": "Rich", "Color": RICH_COLOR},
        {"Label": "Poor", "Color": POOR_COLOR},
        {"Label": "Middle Class", "Color": MID_COLOR},
    ]
)

agent_bar = mesa.visualization.BarChartModule(
    [{"Label": "Wealth", "Color": MID_COLOR}],
    scope="agent",
    sorting="ascending",
    sort_by="Wealth",
)

pie_chart = mesa.visualization.PieChartModule(
    [
        {"Label": "Rich", "Color": RICH_COLOR},
        {"Label": "Middle Class", "Color": MID_COLOR},
        {"Label": "Poor", "Color": POOR_COLOR},
    ]
)

# create instance of Mesa ModularServer
server = mesa.visualization.ModularServer(
    Charts,
    [canvas_element, line_chart, model_bar, agent_bar, pie_chart],
    "Mesa Charts",
    model_params=model_params,
)
