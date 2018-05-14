Best Practices
==============

Here are some general principles that have proven helpful for developing models.

Model Layout
------------

A model should be contained in a folder named with lower-case letters and
underscores, such as ``thunder_cats``. Within that directory:

* ``README.md`` describes the model, how to use it, and any other details.
  Github will automatically show this file to anyone visiting the directory.

* ``requirements.txt`` contains any additional Python distributions, beyond
  Mesa itself, required to run the model.

* ``model.py`` should contain the model class.  If the file gets large, it may
  make sense to move the complex bits into other files, but this is the first
  place readers will look to figure out how the model works.

* ``server.py`` should contain the visualization support, including the server
  class.

* ``run.py`` is a Python script that will run the model when invoked via
  ``mesa run``.

After the number of files grows beyond a half-dozen, try to use sub-folders to
organize them. For example, if the visualization uses image files, put those in
an ``images`` directory.

The `Schelling
<https://github.com/projectmesa/mesa/tree/master/examples/Schelling>`_ model is
a good example of a small well-packaged model.

Randomization
-------------

If your model involves some random choice, you can use either ``random``
(Python's built-in random number generator) or ``numpy.random`` (the generator
included with Numpy).

The constructor for the ``Model`` class automatically "seeds" these random
number generators using the current time, so each run will produce different
random numbers. For testing purposes, it can be helpful to use the same
random-number seed for multiple runs. To accomplish this, pass a value to the
Model constructor:

.. code:: python

    class AwesomeModel(Model):
        def __init__(self, seed=None):
            super().__init__(seed)
            # ...

    model = AwesomeModel(seed=1234)
    # ...

This approach will cause ``RandomActivation`` to activate agents in a
repeatable fashion.
