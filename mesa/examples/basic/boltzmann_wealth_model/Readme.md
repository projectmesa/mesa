# Boltzmann Wealth Model (Tutorial)

## Summary

A simple model of agents exchanging wealth. All agents start with the same amount of money. Every step, each agent with one unit of money or more gives one unit of wealth to another random agent. Mesa's [Getting Started](https://mesa.readthedocs.io/latest/getting_started.html) section walks through the Boltzmann Wealth Model in a series of short introductory tutorials, starting with[Creating your First Model](https://mesa.readthedocs.io/latest/tutorials/0_first_model.html).

As the model runs, the distribution of wealth among agents goes from being perfectly uniform (all agents have the same starting wealth), to highly skewed -- a small number have high wealth, more have none at all.

## How to Run

To run the model interactively, in this directory, run the following command

```
    $ solara run app.py
```

To view and run some example model analyses, launch the IPython Notebook and open ``analysis.ipynb``. Visualizing the analysis also requires [matplotlib](http://matplotlib.org/).

## Files

* ``model.py``: Final version of the model.
* ``agents.py``: Final version of the agent.
* ``app.py``: Code for the interactive visualization.

## Optional

An optional visualization is also provided using Streamlit, which is another popular Python library for creating interactive web applications.

To run the Streamlit app, you will need to install the `streamlit` and `altair` libraries:

```
    $ pip install streamlit altair
```

Then, you can run the Streamlit app using the following command:

```
    $ streamlit run st_app.py
```

## Further Reading

This model is drawn from econophysics and presents a statistical mechanics approach to wealth distribution. Some examples of further reading on the topic can be found at:

[Milakovic, M. A Statistical Equilibrium Model of Wealth Distribution. February, 2001.](https://editorialexpress.com/cgi-bin/conference/download.cgi?db_name=SCE2001&paper_id=214)

[Dragulescu, A and Yakovenko, V. Statistical Mechanics of Money, Income, and Wealth: A Short Survey. November, 2002](http://arxiv.org/pdf/cond-mat/0211175v1.pdf)
