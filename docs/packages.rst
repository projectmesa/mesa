.. _Mesa-Packages:

"How To" Mesa Packages
======================

The Mesa core functionality is just a subset of what we believe researchers creating Agent Based Models (ABMs) will use. We designed Mesa to be extensible, so that individuals from various domains can build and maintain their own Mesa packages in pursuit of "unifying algorithmic theories of the relation between adaptive behavior and system complexity." (Volker Grimm et al 2005)

The purpose of this guide is to support new programmers by providing detailed guides on "How to" build and share a package. Let's get started!


User Guide
-------------------------

**MESA does not endorse or verify any of the code shared through MESA packages**


Use a Package in two Steps
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This "How-To" Guide is based on packages loaded into GitHub

1. Create a virtual environment for the ABM you are building.

	- `Why a virtual environment <https://realpython.com/blog/python/python-virtual-environments-a-primer/#why-the-need-for-virtual-environments>`_
	- `How to create a python virtualenv <http://docs.python-guide.org/en/latest/dev/virtualenvs/#make-sure-you-ve-got-python-pip>`_
 	- `Creating a virtual environment with Anaconda <https://conda.io/docs/user-guide/tasks/manage-environments.html>`_

2. Install the package(s) into your environment via pip and github

	.. code:: bash

		pip install git+https://<enter your clone url from git here>



Package Development: A "How-to Guide"
------------------------------------------------

The purpose of this page is help you set up and distribute your Mesa package as quickly as possible.

This "How-to Guide" uses GitHub to walk you through the process. However, other repositories (e.g. Mecurial, Bitbucket, Beanstalk) will be able to provide similar services.

Package Development Checklist: Sharing your package in seven steps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Take your package from your ABM and make sure it is callable from Mesa in a simple, easy to understand way

2. Think about the structure of your package

   Not sure what this means, see a discussion on package struture at `Hitchhiker's Guide to Python <http://docs.python-guide.org/en/latest/writing/structure/>`_

3. Using GitHub, create a new repository

A. Name your repository
B. Select a license (not sure-- click the blue 'i' next to the i for a great run down of licenses)
C. Create a readme.md file (this contains a description of the package) see an example: `Bilateral Shapley <https://github.com/tpike3/bilateralshapley/blob/master/README.md>`_


4. COMMIT a requirements.txt to the repository

- This can be created automatically from your python environment using the command:

   .. code:: bash

      pip freeze > requirements.txt

- If using Anaconda install pip first

   .. code:: bash

      conda install pip

- For more information on environments see the user guide: :ref:`user-guide`

5. COMMIT a setup.py file

      Python Package Authority Setup `Example <https://github.com/pypa/sampleproject/blob/master/setup.py>`_
      or start with a set up file from a package you like

6. COMMIT the module(s) or folder(s) to the git hub repository

      Don't forgot to follow a good `structure <http://docs.python-guide.org/en/latest/writing/structure/>`_

7. Let people know about your package on the MESA wiki page

      `MESA Wiki Page <https://github.com/projectmesa/mesa/wiki>`_

Take Your Package to the Next Level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You want to do even more. The authoritative guide for python package development is through the `Python Packaging User Guide <https://packaging.python.org/>`_. This will take you through the entire process necessary for getting your package on the Python Package Index.

The `Python Package Index <https://pypi.org>`_ is the main repository of software for Python Packages and following this guide will ensure your code and documentation meets the standards for distribution across the Python community.



