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

Getting started quickly:

```bash
pip install mesa
```

To launch an example model, clone the [repository](https://github.com/projectmesa/mesa) folder and invoke `mesa runserver` for one of the `examples/` subdirectories:

```bash
mesa runserver examples/wolf_sheep
```

For more help on using Mesa, check out the following resources:

- [Mesa Introductory Tutorial]
- [Mesa Visualization Tutorial]
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
Best Practices <best-practices>
How-to Guide <howto>
API Documentation <apis/api_main>
Mesa Packages <packages>
tutorials/adv_tutorial_legacy.ipynb
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
[mesa introductory tutorial]: tutorials/intro_tutorial
[mesa visualization tutorial]: tutorials/visualization_tutorial
[pypi]: https://pypi.python.org/pypi/Mesa/
[ticket]: https://github.com/projectmesa/mesa/issues
