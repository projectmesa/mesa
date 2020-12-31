issue: Optional title in ChartModule #954

mesa.visualization.modules package
==================================

Submodules
----------

mesa.visualization.modules.ChartVisualization module
----------------------------------------------------
Extra parameter "chart_title" added to ChartModule __init__() . 

mesa\visualization\templates\js\ChartModule.js
----------------------------------------------------
ChartModule() signature modified to receive chart_title
js code to insert title added within chartOptions variable

Using the new feature
----------------------------------------------------
Within server class, add chart title as below to an existing ChartModule call:

line_chart = ChartModule(
    [
        {"Label": "Rich", "Color": RICH_COLOR},
        {"Label": "Poor", "Color": POOR_COLOR},
        {"Label": "Middle Class", "Color": MID_COLOR},
    ],chart_title = "line chart"
)

Code block modified in \mesa\examples\charts\charts\server.py for testing.

