# Mesa: Agent-based modeling in Python

```{image} https://github.com/projectmesa/mesa/workflows/build/badge.svg
:target: https://github.com/projectmesa/mesa/actions
```

```{image} https://codecov.io/gh/projectmesa/mesa/branch/main/graph/badge.svg
:target: https://codecov.io/gh/projectmesa/mesa
```

```{image} https://img.shields.io/badge/code%20style-black-000000.svg
:target: https://github.com/psf/black
```

```{image} https://img.shields.io/matrix/project-mesa:matrix.org?label=chat&logo=Matrix
:target: https://matrix.to/#/#project-mesa:matrix.orgs
```

[Mesa] is an Apache2 licensed agent-based modeling (or ABM) framework in Python.

The original conference paper is [available here](http://conference.scipy.org.s3-website-us-east-1.amazonaws.com/proceedings/scipy2015/jacqueline_kazil.html).

Mesa allows users to quickly create agent-based models using built-in core components (such as spatial grids and agent schedulers) or customized implementations; visualize them using a browser-based interface; and analyze their results using Python's data analysis tools. Its goal is to be the Python-based counterpart to NetLogo, Repast, or MASON.


![A screenshot of the Schelling Model in Mesa|100%](https://raw.githubusercontent.com/projectmesa/mesa/main/docs/images/Mesa_Screenshot.png)


*Above: A Mesa implementation of the Schelling segregation model,
being visualized in a browser window and analyzed in a Jupyter
notebook.*

## Features

- Modular components
- Browser-based visualization
- Built-in tools for analysis

## Using Mesa

To install our latest stable release (2.4.x), run:

``` bash
pip install -U mesa
```

Mesa >= 3.0 beta includes several installations options:

``` bash
pip install -U --pre mesa[rec]
```
**mesa[rec]** (recommend install) installs - mesa, [networkx](https://networkx.org/), [matplotlib](https://matplotlib.org/stable/install/index.html)
and [solara](https://solara.dev/)

### Other installation options include:

- **mesa[network]** installs mesa and [networkx](https://networkx.org/)
- **mesa[viz]** installs, mesa, [matplotlib](https://matplotlib.org/stable/install/index.html) and [solara](https://solara.dev/)
- **mesa[dev]** installs mesa[rec], [ruff](https://docs.astral.sh/ruff/), [pytest](https://docs.pytest.org/en/stable/), [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/), [sphinx](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#cmdoption-sphinx-build-e), [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/), [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/)
- **mesa[examples]** installs mesa[rec], [pytest](https://docs.pytest.org/en/stable/), and [scipy](https://scipy.org/)
- **mesa[docs]** installs mesa[rec], [sphinx](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#cmdoption-sphinx-build-e), [ipython](https://ipython.readthedocs.io/en/stable/install/kernel_install.html), [pydata_sphinx_theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/),
[seaborn](https://seaborn.pydata.org/), [myst-nb](https://myst-nb.readthedocs.io/en/latest/), [myst-parser](https://myst-parser.readthedocs.io/en/latest/)

Then mesa[all] installs all these sub installation options:
**mesa[all]** = mesa[network,viz,dev,examples,docs]

For more help on using Mesa, check out the following resources:

- [Mesa Overview]
- [Mesa Introductory Tutorial]
- [Mesa Visualization Tutorial]
- [Mesa Examples]
- [GitHub Issue Tracker]
- [Matrix chat room]
- [PyPI]

## Contributing back to Mesa

If you run into an issue, please file a [ticket] for us to discuss. If possible, follow up with a pull request.

If you would like to add a feature, please reach out via [ticket] or the [email list] for discussion. A feature is most likely to be added if you build it!

- [Contributors guide]
- [Github]

## Mesa Packages

ABM features users have shared that you may want to use in your model

- [See the Packages](https://github.com/projectmesa/mesa/wiki)
- {ref}`Mesa-Packages <packages>`

```{toctree}
:hidden: true
:maxdepth: 7

Mesa Overview <overview>
tutorials/intro_tutorial
tutorials/visualization_tutorial
Examples <examples>
Migration guide <migration_guide>
Best Practices <best-practices>
How-to Guide <howto>
API Documentation <apis/api_main>
Mesa Packages <packages>
```

# Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`

[contributors guide]: https://github.com/projectmesa/mesa/blob/main/CONTRIBUTING.md
[github]: https://github.com/projectmesa/mesa/
[github issue tracker]: https://github.com/projectmesa/mesa/issues
[matrix chat room]: https://matrix.to/#/#project-mesa:matrix.org
[mesa]: https://github.com/projectmesa/mesa/
[mesa overview]: overview
[mesa examples]: https://github.com/projectmesa/mesa-examples
[mesa introductory tutorial]: tutorials/intro_tutorial
[mesa visualization tutorial]: tutorials/visualization_tutorial
[pypi]: https://pypi.python.org/pypi/Mesa/
[ticket]: https://github.com/projectmesa/mesa/issues
