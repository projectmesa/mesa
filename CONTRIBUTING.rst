Contributing
=========================

As an open source project, Mesa welcomes contributions of many forms.

In no particular order, examples include:

- Code patches
- Bug reports and patch reviews
- New features
- Documentation improvements
- Tutorials

No contribution is too small. Although, contributions can be too big, so let's discuss via the `dev email list`_ OR `an issue`_.

.. _`dev email list` : https://groups.google.com/forum/#!forum/projectmesa-dev
.. _`an issue` : https://github.com/projectmesa/mesa/issues

**To submit a contribution**

- Create a ticket for the item that you are working on.
- Fork the Mesa repository.
- `Clone your repository`_ from Github to your machine.
- Create a new branch in your fork: ``git checkout -b BRANCH_NAME``
- Install an editable version with developer requirements locally: ``pip install -e .[dev]``
- Edit the code. Save.
- Git add the new files and files with changes: ``git add FILE_NAME``
- Git commit your changes with a meaningful message: ``git commit -m "Fixes X issue."``
- If implementing a new feature, include some documentation in docs folder.
- Make sure that your submission passes the `Travis build`_. See "Testing and Standards below" to be able to run these locally.
- Push your changed to your fork on Github: ``git push origin NAME_OF_BRANCH``.
- `Create a pull request`_.
- Describe the change w/ ticket number(s) that the code fixes.

.. _`Clone your repository` : https://help.github.com/articles/cloning-a-repository/
.. _`Travis build` : https://travis-ci.org/projectmesa/mesa
.. _`Create a pull request` : https://help.github.com/articles/creating-a-pull-request/



Testing and Code Standards
--------

.. image:: https://codecov.io/gh/projectmesa/mesa/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/projectmesa/mesa

As part of our contribution process, we practice continuous integration and use Travis to help enforce best practices.

If you're changing previous Mesa features, please make sure of the following:

- Your changes pass the current tests.
- Your changes pass our style standards.
- Your changes don't break the models or your changes include updated models.
- Additional features or rewrites of current features are accompanied by tests.
- New features are demonstrated in a model, so folks can understand more easily.

To ensure that your submission will not break the build, you will need to install Flake8 and Nose.

.. code-block:: bash

    pip install flake8 pytest pytest-cov

We test by implementing simple models and through traditional unit tests in the tests/ folder. The following only covers unit tests coverage. Ensure that your test coverage has not gone down. If it has and you need help, we will offer advice on how to structure tests for the contribution.

.. code-block:: bash

    py.test --cov=mesa tests/

With respect to code standards, we follow `PEP8`_ and the `Google Style Guide`_. If the command below generates errors, fix all errors that are returned.

.. code-block:: bash

    flake8 . --ignore=F403,E501,E123,E128,W504 --exclude=docs,build

.. _`PEP8` : https://www.python.org/dev/peps/pep-0008
.. _`Google Style Guide` : https://google.github.io/styleguide/pyguide.html


Licensing
--------

The license of this project is located in `LICENSE`_.  By submitting a contribution to this project, you are agreeing that your contribution will be released under the terms of this license.

.. _`LICENSE` : https://github.com/projectmesa/mesa/blob/master/LICENSE


Special Thanks
--------

A special thanks to the following projects who offered inspiration for this contributing file.

- `Django`_
- `18F's FOIA`_
- `18F's Midas`_

.. _`Django` : https://github.com/django/django/blob/master/CONTRIBUTING.rst
.. _`18F's FOIA` : https://github.com/18F/foia-hub/blob/master/CONTRIBUTING.md
.. _`18F's Midas` : https://github.com/18F/midas/blob/devel/CONTRIBUTING.md
