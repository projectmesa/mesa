# Boltzmann Wealth Model (Tutorial)

## Summary

A simple model of agents exchanging wealth. All agents start with the same amount of money. Every step, each agent with one unit of money or more gives one unit of wealth to another random agent. This is the model described in the [Intro Tutorial](http://mesa.readthedocs.io/en/latest/intro-tutorial.html).

As the model runs, the distribution of wealth among agents goes from being perfectly uniform (all agents have the same starting wealth), to highly skewed -- a small number have high wealth, more have none at all.

## How to Run

To follow the tutorial examples, launch the Jupyter Notebook and run the code in ``Introduction to Mesa Tutorial Code.ipynb``.

To launch the interactive server, as described in the [last section of the tutorial](http://mesa.readthedocs.io/en/latest/intro-tutorial.html#adding-visualization), run:

```
    $ python viz_money_model.py
```

If your browser doesn't open automatically, point it to [http://127.0.0.1:8521/](http://127.0.0.1:8521/). When the visualization loads, press Reset, then Run.


## Files

* ``Introduction to Mesa Tutorial Code.ipynb``: Jupyter Notebook with all the steps as described in the tutorial.
* ``money_model.py``: Final version of the model.
* ``viz_money_model.py``: Creates and launches interactive visualization.

## Further Reading

The full tutorial describing how the model is built can be found at:
http://mesa.readthedocs.io/en/latest/intro-tutorial.html

This model is drawn from econophysics and presents a statistical mechanics approach to wealth distribution. Some examples of further reading on the topic can be found at:

[Milakovic, M. A Statistical Equilibrium Model of Wealth Distribution. February, 2001.](https://editorialexpress.com/cgi-bin/conference/download.cgi?db_name=SCE2001&paper_id=214)

[Dragulescu, A and Yakovenko, V. Statistical Mechanics of Money, Income, and Wealth: A Short Survey. November, 2002](http://arxiv.org/pdf/cond-mat/0211175v1.pdf)
____
You will need to open the file as a Jupyter (aka iPython) notebook with an iPython 3 kernel. Required dependencies are listed in the provided `requirements.txt` file which can be installed by running `pip install -r requirements.txt`
