# Mesa: Agent-based modeling in Python

| | |
| --- | --- |
| CI/CD | [![GitHub Actions build status](https://github.com/projectmesa/mesa/workflows/build/badge.svg)](https://github.com/projectmesa/mesa/actions) [![Coverage status](https://codecov.io/gh/projectmesa/mesa/branch/main/graph/badge.svg)](https://codecov.io/gh/projectmesa/mesa) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/mesa.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/Mesa/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/mesa.svg?color=blue&label=Downloads&logo=pypi&logoColor=gold)](https://pypi.org/project/Mesa/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mesa.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/Mesa/) |
| Meta | [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![SPEC 0 — Minimum Supported Dependencies](https://img.shields.io/badge/SPEC-0-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0000/) |
| Chat | [![chat](https://img.shields.io/matrix/project-mesa:matrix.org?label=chat&logo=Matrix)](https://matrix.to/#/#project-mesa:matrix.org) |

Mesa allows users to quickly create agent-based models using built-in
core components (such as spatial grids and agent schedulers) or
customized implementations; visualize them using a browser-based
interface; and analyze their results using Python's data analysis
tools. Its goal is to be the Python-based alternative to NetLogo,
Repast, or MASON.

![A screenshot of the WolfSheep Model in Mesa](https://raw.githubusercontent.com/projectmesa/mesa/main/docs/images/wolf_sheep.png)

*Above: A Mesa implementation of the WolfSheep model, this
can be displayed in browser windows or Jupyter.*

## Features

-   Modular components
-   Browser-based visualization
-   Built-in tools for analysis
-   Example model library

## Using Mesa

To install our latest stable release, run:

``` bash
pip install -U mesa
```

Starting with Mesa 3.0, we don't install all our dependencies anymore by default.
```bash
# You can customize the additional dependencies you need, if you want. Available are:
pip install -U mesa[network,viz]

# This is equivalent to our recommended dependencies:
pip install -U mesa[rec]

# To install all, including developer, dependencies:
pip install -U mesa[all]
```

You can also use `pip` to install the latest GitHub version:

``` bash
pip install -U -e git+https://github.com/projectmesa/mesa@main#egg=mesa
```

Or any other (development) branch on this repo or your own fork:

``` bash
pip install -U -e git+https://github.com/YOUR_FORK/mesa@YOUR_BRANCH#egg=mesa
```

## Resources
For resources or help on using Mesa, check out the following:

-   [Intro to Mesa Tutorial](http://mesa.readthedocs.org/en/stable/tutorials/intro_tutorial.html) (An introductory model, the Boltzmann
    Wealth Model, for beginners or those new to Mesa.)
-   [Visualization Tutorial](https://mesa.readthedocs.io/stable/tutorials/visualization_tutorial.html) (An introduction into our Solara visualization)
-   [Complexity Explorer Tutorial](https://www.complexityexplorer.org/courses/172-agent-based-models-with-python-an-introduction-to-mesa) (An advanced-beginner model,
    SugarScape with Traders, with instructional videos)
-   [Mesa Examples](https://github.com/projectmesa/mesa-examples) (A repository of seminal ABMs using Mesa and
    examples of employing specific Mesa Features)
-   [Docs](http://mesa.readthedocs.org/) (Mesa's documentation, API and useful snippets)
    -   [Development version docs](https://mesa.readthedocs.io/latest/) (the latest version docs if you're using a pre-release Mesa version)
-   [Discussions](https://github.com/projectmesa/mesa/discussions) (GitHub threaded discussions about Mesa)
-   [Matrix Chat](https://matrix.to/#/#project-mesa:matrix.org) (Chat Forum via Matrix to talk about Mesa)

## Running Mesa in Docker

You can run Mesa in a Docker container in a few ways.

If you are a Mesa developer, first [install Docker
Compose](https://docs.docker.com/compose/install/) and then, in the
folder containing the Mesa Git repository, you run:

``` bash
$ docker compose up
# If you want to make it run in the background, you instead run
$ docker compose up -d
```

This runs the Schelling model, as an example.

With the docker-compose.yml file in this Git repository, the `docker compose up` command does two important things:

-   It mounts the mesa root directory (relative to the
    docker-compose.yml file) into /opt/mesa and runs pip install -e on
    that directory so your changes to mesa should be reflected in the
    running container.
-   It binds the docker container's port 8765 to your host system's
    port 8765 so you can interact with the running model as usual by
    visiting localhost:8765 on your browser

If you are a model developer that wants to run Mesa on a model, you need
to:

-   make sure that your model folder is inside the folder containing the
    docker-compose.yml file
-   change the `MODEL_DIR` variable in docker-compose.yml to point to
    the path of your model
-   make sure that the model folder contains an app.py file

Then, you just need to run `docker compose up -d` to have it
accessible from `localhost:8765`.

## Contributing to Mesa

Want to join the Mesa team or just curious about what is happening with
Mesa? You can\...

> -   Join our [Matrix chat room](https://matrix.to/#/#project-mesa:matrix.org) in which questions, issues, and
>     ideas can be (informally) discussed.
> -   Come to a monthly dev session (you can find dev session times,
>     agendas and notes on [Mesa discussions](https://github.com/projectmesa/mesa/discussions)).
> -   Just check out the code on [GitHub](https://github.com/projectmesa/mesa/).

If you run into an issue, please file a [ticket](https://github.com/projectmesa/mesa/issues) for us to discuss. If
possible, follow up with a pull request.

If you would like to add a feature, please reach out via [ticket](https://github.com/projectmesa/mesa/issues) or
join a dev session (see [Mesa discussions](https://github.com/projectmesa/mesa/discussions)). A feature is most likely
to be added if you build it!

Don't forget to checkout the [Contributors guide](https://github.com/projectmesa/mesa/blob/main/CONTRIBUTING.md).

## Citing Mesa

To cite Mesa in your publication, you can use the [CITATION.bib](https://github.com/projectmesa/mesa/blob/main/CITATION.bib).
