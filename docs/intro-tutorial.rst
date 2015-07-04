Introduction to Mesa - Tutorial
================================

Getting started with Mesa is easy. In this doc, we will present Mesa’s
architecture and core features. To illustrate their use, we will describe and build a simple agent-based model, drawn from econophysics and presenting a statistical mechanics approach to wealth distribution [Dragulescu2002]_.

The rules of our tutorial model:

- There are some number of agents.
- All agents begin with 1 unit of money.
- Every step fo the model, an agent gives 1 unit of money (if they have it) to some other agent.

Despite its simplicity, this model yields results that are often unexpected to those not familiar with it. For our purposes, it also easily demonstrates Mesa's core features.

Let's get started.


Installation
------------

The first thing you need to do is to install Mesa. We recommend doing this in a `virtual environment`_. Make sure your work space is pointed to Python3. Mesa requires Python3 and does not work in < Python3 environments.

To install Mesa, simply:

.. code-block:: bash

    $ pip install mesa

When you do that, it will install the following packages and dependencies.

- mesa
- tornado
- numpy
- pandas


** THIS DOC IS IN PROGRESS **




.. _`virtual environment`: http://docs.python-guide.org/en/latest/dev/virtualenvs/

.. [Dragulescu2002] Drăgulescu, Adrian A., and Victor M. Yakovenko. “Statistical Mechanics of Money, Income, and Wealth: A Short Survey.” arXiv Preprint Cond-mat/0211175, 2002. http://arxiv.org/abs/cond-mat/0211175.



