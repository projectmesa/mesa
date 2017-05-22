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
  place readers will look to figure out how the model lworks.

* ``run.py`` is a Python script that will run the model when invoked as
  ``python run.py``.

After the number of files grows beyond a half-dozen, try to use sub-folders to
organize them. For example, if the visualization uses image files, put those in
an ``images`` directory.

The `Schelling
<https://github.com/projectmesa/mesa/tree/master/examples/Schelling>`_ model is
a good example of a small well-packaged model.
