"How To" Mesa Packages
======================

The Mesa core functionality is just a subset of what we believe researchers creating Agent Based Models (ABMs) will use. We designed Mesa to be extensible, so that individuals from various domains can build, maintain, and share their own packages that work with Mesa in pursuit of "unifying algorithmic theories of the relation between adaptive behavior and system complexity (Volker Grimm et al 2005)."

**DRY Principal**

This decoupling of code to create building blocks is a best practice in software engineering. Specifically, it exercises the `DRY principal (or don't repeat yourself.) <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_. The creators of Mesa designed Mesa in order for this principal to be exercised in the development of agent-based models (ABMs). For example, a group health experts may create a library of human interactions on top of core Mesa. That library then is used by other health experts. So, those health experts don't have to rewrite the same basic behaviors.

**Benefits to Scientists**

Besides a best practice of the software engineering community, there are other benefits for the scientific community.

1. **Reproducibility.** Decoupled shared packages also allows for reproducibility. Having a package that is shared allows others to test the methods that lead to the model results that the researcher arrived at.

2. **Accepted truths.** Once results are reproduced, a library could be considered an accepted truth, meaning that the community agrees that the library does what the library intends to do and that the library can be trusted to do this. Part of the idea behind 'accepted truths' is that subject matter experts are the ones that write and maintain the library.

2. **Building blocks.** Think of libraries like Legos. The researcher can borrow a piece from here or there to pull together the base of their model, so they can focus on the value add that they bring. For example, someone might pull from a human interactions library and a decision-making library and combine the two to look at how human cognitive function effects the physical spread of disease.

**Mesa and Mesa Packages**

Because of the possibilities of nuanced libraries, few things will actually make it into core Mesa. Mesa is intended to only include core functionality that everyone uses. However, it is not impossible that something written on the outside is brought into core at a later date if the value to everyone is proven through adoption.

An example that is analogous to Mesa and Mesa packages is `Django <https://www.djangoproject.com/>`_ and `Django Packages <https://djangopackages.org/>`_. Django is a web framework that allows you to build a website in Python, but there are lots of things besides a basic website that you might want. For example, you might want authentication functionality. It would be inefficient for everyone to write their own authentication functionality, so one person writes it (or a group of people). They share it with the world and then many people can use it.

This process isn't perfect. Just because you write something doesn't mean people are going to use it. Sometimes two different packages will be created that do similar things, but one of them does it better or is easier to use. That is the one that will get more adoption. In the world of academia, often researchers hold on to their content until they are ready to publish it. In the world of open source software, this can backfire. The sooner you open source something the more likely it will be a success, because you will build consensus and engagement. Another thing that can happen is that while you are working on perfecting it, someone else is building in the open and establishes the audience you were looking for. So, don't be afraid to start working directly out in the open and then release it to the world.

**What is in this doc**

There are two sections in this documention. The first is the User Guide, which is aimed at users of packages. The section is a package development guide, which is aimed at those who want to develop packages. Without further ado, let's get started!


User Guide
-------------------------

* Note: MESA does not endorse or verify any of the code shared through MESA packages. This is left to the domain experts of the community that created the code.*

**Step 1: Establish an environment**

Create a virtual environment for the ABM you are building. The purpose of a virtual environment is to isolate the packages for your project from other projects. This is helpful when you need to use two different versions of a package or if you are running one version in production but want to test out another version. You can do with either virtualenv or Anaconda.

   - `Why a virtual environment <https://realpython.com/blog/python/python-virtual-environments-a-primer/#why-the-need-for-virtual-environments>`_
   - `Virtualenv and Virtualenv Wrapper <http://docs.python-guide.org/en/latest/#python-development-environments>`_
   - `Creating a virtual environment with Anaconda <https://conda.io/docs/user-guide/tasks/manage-environments.html>`_

**Step 2: Install the packages**

Install the package(s) into your environment via pip/conda or GitHub. If the package is a mature package that is hosted in the Python package repository, then you can install it just like you did Mesa:

   .. code:: bash

      pip install package_name

However, sometimes it takes a little bit for projects to reach that level of maturity. In that case to use the library, you would install from GitHub (or other code repository) with something like the following:


   .. code:: bash

      pip install https://github.com/<path to project>

The commands above should also work with Anaconda, just replace the `pip` with `conda`.


Package Development: A "How-to Guide"
------------------------------------------------

The purpose of this page is help you set up and distribute your Mesa package as quickly as possible.

This "How-to Guide" uses GitHub to walk you through the process. However, other repositories (e.g. Mercurial, Bitbucket, Beanstalk) will be able to provide similar services.

Package Development Checklist: Sharing your package in seven steps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Take your package from your ABM and make sure it is callable from Mesa in a simple, easy to understand way

2. Think about the structure of your package

   Not sure what this means, see a discussion on package structure at `Hitchhiker's Guide to Python <http://docs.python-guide.org/en/latest/writing/structure/>`_

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

6. COMMIT the module(s) or folder(s) to the GitHub repository

      Don't forgot to follow a good `structure <http://docs.python-guide.org/en/latest/writing/structure/>`_

7. Let people know about your package on the MESA wiki page

      `MESA Wiki Page <https://github.com/projectmesa/mesa/wiki>`_

Take Your Package to the Next Level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You want to do even more. The authoritative guide for python package development is through the `Python Packaging User Guide <https://packaging.python.org/>`_. This will take you through the entire process necessary for getting your package on the Python Package Index.

The `Python Package Index <https://pypi.org>`_ is the main repository of software for Python Packages and following this guide will ensure your code and documentation meets the standards for distribution across the Python community.

