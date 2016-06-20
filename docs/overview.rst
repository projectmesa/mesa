Overview of Modules
-------------------

Mesa is modular, meaning that There are three module types in Mesa.

1. Modeling
2. Analysis
3. Visualization

TODO: Insert image


Modeling modules
~~~~~~~~~~~~~~~~

To build a model, you need the following:

* **Model class** to store the model-level parameters and serve as a container for the rest of the components.

* **Agent class(es)** which describe the model agents.

* **Scheduler** which controls the agent activation regime, and handles time in the model in general.

* **space** components describing the space and/or network the agents are situated in (if any).


Analysis modules
~~~~~~~~~~~~~~~~

Not every model *needs* these modules, but they provide useful tools for getting data out of your model runs to study more systematically.

* **Data collectors** are used to record data from each model run.
* **Batch runners** automate multiple runs and parameter sweeps -- running the model with different parameters, to see how they change its behavior.


Visualization modules
~~~~~~~~~~~~~~~~~~~~~

A visualization lets you directly observe model runs, seeing the dynamics that emerge from it and making sure that it's behaving in the way you want it to. Mesa handles visualizations in a browser window, using JavaScript. It provides a set of pre-built components, which can be instantiated for a particular model in Python and automatically generate the corresponding objects in the browser window. It's also easy to write your own components with some basic JavaScript knowledge.

Some visualization modules we'll use here include:

* **Grid** visualization,
* **Chart** display module,
* The **ModularServer** itself.
