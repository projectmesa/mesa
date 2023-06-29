# Boltzmann Wealth Model (Tutorial)

## Summary

A simple model of agents exchanging wealth. All agents start with the same amount of money. Every step, each agent with one unit of money or more gives one unit of wealth to another random agent. This is the model described in the [Intro Tutorial](https://mesa.readthedocs.io/en/latest/tutorials/intro_tutorial.html), with the completed code.

If you want to go over the step-by-step tutorial, please go and run the [Jupyter Notebook](https://github.com/projectmesa/mesa/blob/main/docs/tutorials/intro_tutorial.ipynb). The code here runs the finalized code in the last cells directly.

As the model runs, the distribution of wealth among agents goes from being perfectly uniform (all agents have the same starting wealth), to highly skewed -- a small number have high wealth, more have none at all.

## How to Run

To follow the tutorial example, launch the Jupyter Notebook and run the code in ``Introduction to Mesa Tutorial Code.ipynb`` which you can find in the main mesa repo [here](https://github.com/projectmesa/mesa/blob/main/docs/tutorials/intro_tutorial.ipynb)

To launch the interactive server, as described in the [last section of the tutorial](https://mesa.readthedocs.io/en/latest/tutorials/intro_tutorial.html#adding-visualization), run:

```
    $ python server.py
```

Make sure to install the requirements first:

```
    pip install -r requirements.txt
```

If your browser doesn't open automatically, point it to [http://127.0.0.1:8521/](http://127.0.0.1:8521/). When the visualization loads, press Reset, then Run.


## Files

* ``boltzmann_wealth_model/model.py``: Final version of the model.
* ``boltzmann_wealth_model/server.py``: Code for the interactive visualization.
* ``run.py``: Launches the server.

## Optional

*  ``boltzmann_wealth_model/app.py``: can be used to run the simulation via the streamlit interface.
* For this some additional packages like ``streamlit`` and ``altair`` needs to be installed.
* Once installed, the app can be opened in the browser using : ``streamlit run app.py``

## Further Reading

The full tutorial describing how the model is built can be found at:
https://mesa.readthedocs.io/en/latest/tutorials/intro_tutorial.html

This model is drawn from econophysics and presents a statistical mechanics approach to wealth distribution. Some examples of further reading on the topic can be found at:

[Milakovic, M. A Statistical Equilibrium Model of Wealth Distribution. February, 2001.](https://editorialexpress.com/cgi-bin/conference/download.cgi?db_name=SCE2001&paper_id=214)

[Dragulescu, A and Yakovenko, V. Statistical Mechanics of Money, Income, and Wealth: A Short Survey. November, 2002](http://arxiv.org/pdf/cond-mat/0211175v1.pdf)
