Mesa: Agent-based modeling in Python 3+
=========================================

.. image:: https://api.travis-ci.org/projectmesa/mesa.svg?branch=master
        :target: https://travis-ci.org/projectmesa/mesa

.. image:: https://codecov.io/gh/projectmesa/mesa/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/projectmesa/mesa

`Mesa`_ is an Apache2 licensed agent-based modeling (or ABM) framework in Python.

It allows users to quickly create agent-based models using built-in core components (such as spatial grids and agent schedulers) or customized implementations; visualize them using a browser-based interface; and analyze their results using Python's data analysis tools. Its goal is to be the Python 3-based alternative to NetLogo, Repast, or MASON.


.. image:: https://github.com/projectmesa/mesa/blob/master/docs/images/Mesa_Screenshot.png
   :width: 100%
   :scale: 100%
   :alt: A screenshot of the Schelling Model in Mesa

*Above: A Mesa implementation of the Schelling segregation model,
being visualized in a browser window and analyzed in a Jupyter
notebook.*

.. _`Mesa` : https://github.com/projectmesa/mesa/


Features
------------

* Modular components
* Browser-based visualization
* Built-in tools for analysis
* Example model library

Using Mesa
------------

Getting started quickly:

.. code-block:: bash

    $ pip install mesa

You can also use `pip` to install the github version:

.. code-block:: bash

    $ pip install -e git+https://github.com/projectmesa/mesa#egg=mesa

Take a look at the `examples <https://github.com/projectmesa/mesa/tree/master/examples>`_ folder for sample models demonstrating Mesa features.

For more help on using Mesa, check out the following resources:

* `Intro to Mesa Tutorial`_
* `Docs`_
* `Email list for users`_
* `PyPI`_

.. _`Intro to Mesa Tutorial` : http://mesa.readthedocs.org/en/master/tutorials/intro_tutorial.html
.. _`Docs` : http://mesa.readthedocs.org/en/master/
.. _`Email list for users` : https://groups.google.com/d/forum/projectmesa
.. _`PyPI` : https://pypi.python.org/pypi/Mesa/

Running Mesa in Docker
------------------------

You can run Mesa in a Docker container in a few ways.

If you are a Mesa developer, first `install docker-compose <https://docs.docker.com/compose/install/>`_ and then run:

.. code-block:: bash

    $ docker-compose build --pull
    ...
    $ docker-compose up -d dev # start the docker container
    $ docker-compose exec dev bash # enter the docker container that has your current version of Mesa installed at /opt/mesa
    $ mesa runserver examples/Schelling # or any other example model in examples


The docker-compose file does two important things:

* It binds the docker container's port 8521 to your host system's port 8521 so you can interact with the running model as usual by visiting localhost:8521 on your browser
* It mounts the mesa root directory (relative to the docker-compose.yml file) into /opt/mesa and runs pip install -e on that directory so your changes to mesa should be reflected in the running container.


If you are a model developer that wants to run Mesa on a model (assuming you are currently in your top-level model
directory with the run.py file):

.. code-block:: bash

    $ docker run --rm -it -p127.0.0.1:8521:8521 -v${PWD}:/code comses/mesa:dev mesa runserver /code

Contributing back to Mesa
----------------------------

If you run into an issue, please file a `ticket`_ for us to discuss. If possible, follow up with a pull request.

If you would like to add a feature, please reach out via `ticket`_ or the `dev email list`_ for discussion. A feature is most likely to be added if you build it!

* `Contributors guide`_
* `Github`_

.. _`ticket` : https://github.com/projectmesa/mesa/issues
.. _`dev email list` : https://groups.google.com/forum/#!forum/projectmesa-dev
.. _`Contributors guide` : https://github.com/projectmesa/mesa/blob/master/CONTRIBUTING.rst
.. _`Github` : https://github.com/projectmesa/mesa/
