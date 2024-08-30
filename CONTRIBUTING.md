# Contributing

As an open source project, Mesa welcomes contributions of many forms, and from beginners to experts. If you are
curious or just want to see what is happening, we post our development session agendas
and development session notes on [Mesa discussions]. We also have a threaded discussion forum on [Matrix]
for casual conversation.

In no particular order, examples include:

- Code patches
- Bug reports and patch reviews
- New features
- Documentation improvements
- Tutorials

No contribution is too small. Although, contributions can be too big, so let's
discuss via [Matrix] OR via [an issue].

**To submit a contribution**

- Create a ticket for the item that you are working on.
- Fork the Mesa repository.
- [Clone your repository] from Github to your machine.
- Create a new branch in your fork: `git checkout -b BRANCH_NAME`
- Run `git config pull.rebase true`. This prevents messy merge commits when updating your branch on top of Mesa main branch.
- Install an editable version with developer requirements locally: `pip install -e ".[dev]"`
- Edit the code. Save.
- Git add the new files and files with changes: `git add FILE_NAME`
- Git commit your changes with a meaningful message: `git commit -m "Fix issue X"`
- If implementing a new feature, include some documentation in docs folder.
- Make sure that your submission works with a few of the examples in the examples repository. If adding a new feature to mesa, please illustrate usage by implementing it in an example.
- Make sure that your submission passes the [GH Actions build]. See "Testing and Standards below" to be able to run these locally.
- Make sure that your code is formatted according to [the black] standard (you can do it via [pre-commit]).
- Push your changes to your fork on Github: `git push origin NAME_OF_BRANCH`.
- [Create a pull request].
- Describe the change w/ ticket number(s) that the code fixes.
- Format your commit message as per [Tim Pope's guideline].

## I have no idea where to start
That's fine! Here's a rough outline where you could start, depending on your experience:

### I'm a modeller (but not an experienced developer)
You already know how to build Mesa models (if not skip below), and probably have found things Mesa can't do (elegantly). You want to improve that. Awesome!

First step is to install some proper tools, if you haven't already.
- A good IDE helps for code development, testing and formatting. [PyCharm](https://www.jetbrains.com/pycharm/) or [VSCode](https://code.visualstudio.com/) for example.
- Dive into Git and GitHub. Watch some videos, this takes some time to click. [GitHub Desktop](https://desktop.github.com/) is great.
- [`https://github.dev/projectmesa/mesa`](https://github.dev/projectmesa/mesa) is great for small changes (to docs).

Learn the tools, talk to us about what you want to change, and open a small PR. Or update an [example model](https://github.com/projectmesa/mesa-examples) (check open [issues](https://github.com/projectmesa/mesa-examples/issues))!

### I'm a developer (but not a modeller)
Awesome! You have the basics of open-source software development (if not check above), but not much modelling experience.

First step is to start thinking like a modeller. To understand the fine details about our library and contribute meaningfully, get some modelling experience:
- Go though our [Introductory Tutorial](https://mesa.readthedocs.io/en/latest/tutorials/intro_tutorial.html) and [Visualization Tutorial](https://mesa.readthedocs.io/en/latest/tutorials/visualization_tutorial.html). While going through them, dive into the source code to really see what everything does.
- Follow an ABM course (if possible). They might be a bit outdated programming language wise, but conceptual they're sound.
  - This MOOC on ABM concepts: [Agent Based Modeling](https://ocw.tudelft.nl/course-lectures/agent-based-modeling/)
  - This MOOC on practical ABM modelling: [Agent-Based Models with Python: An Introduction to Mesa](https://www.complexityexplorer.org/courses/172-agent-based-models-with-python-an-introduction-to-mesa)
- Go though multiple of our [examples](https://github.com/projectmesa/mesa-examples). Play with them, modify things and get a feel for Mesa and ABMs.
  - Check our open [issues](https://github.com/projectmesa/mesa-examples/issues) for the examples.
  - If you see anything you want to improve, feel free to open a (small) PR!
- If you have a feel for Mesa, check our [discussions](https://github.com/projectmesa/mesa/discussions) and [issues](https://github.com/projectmesa/mesa/issues).
  - Also go thought our [release notes](https://github.com/projectmesa/mesa/releases) to see what we recently have been working on, and see some examples of successful PRs.
- Once you found or thought of a nice idea, comment on the issue/discussion (or open a new one) and get to work!

### I'm both
That's great! You can just start working on things, reach out to us. Skim to the list above if you feel you're missing anything. Start small but don't be afraid to dream big!

### I'm neither
Start with creating your own models, for fun. Once you have some experience, move to the topics above.

## Testing and Code Standards

```{image} https://codecov.io/gh/projectmesa/mesa/branch/main/graph/badge.svg
:target: https://codecov.io/gh/projectmesa/mesa
```

```{image} https://img.shields.io/badge/code%20style-black-000000.svg
:target: https://github.com/psf/black
```

As part of our contribution process, we practice continuous integration and use GH Actions to help enforce best practices.

If you're changing previous Mesa features, please make sure of the following:

- Your changes pass the current tests.
- Your changes pass our style standards.
- Your changes don't break the models or your changes include updated models.
- Additional features or rewrites of current features are accompanied by tests.
- New features are demonstrated in a model, so folks can understand more easily.

To ensure that your submission will not break the build, you will need to install Ruff and pytest.

```bash
pip install ruff pytest pytest-cov
```

We test by implementing simple models and through traditional unit tests in the tests/ folder. The following only covers unit tests coverage. Ensure that your test coverage has not gone down. If it has and you need help, we will offer advice on how to structure tests for the contribution.

```bash
py.test --cov=mesa tests/
```

With respect to code standards, we follow [PEP8] and the [Google Style Guide]. We use [ruff format] (a more performant alternative to `black`) as an automated code formatter. You can automatically format your code using [pre-commit], which will prevent `git commit` of unstyled code and will automatically apply black style so you can immediately re-run `git commit`. To set up pre-commit run the following commands:

```bash
pip install pre-commit
pre-commit install
```

You should no longer have to worry about code formatting. If still in doubt you may run the following command. If the command generates errors, fix all errors that are returned.

```bash
ruff .
```

## Licensing

The license of this project is located in [LICENSE].  By submitting a contribution to this project, you are agreeing that your contribution will be released under the terms of this license.

## Special Thanks

A special thanks to the following projects who offered inspiration for this contributing file.

- [Django]
- [18F's FOIA]
- [18F's Midas]

[18f's foia]: https://github.com/18F/foia-hub/blob/master/CONTRIBUTING.md
[18f's midas]: https://github.com/18F/midas/blob/devel/CONTRIBUTING.md
[an issue]: https://github.com/projectmesa/mesa/issues
[black]: https://github.com/psf/black
[clone your repository]: https://help.github.com/articles/cloning-a-repository/
[create a pull request]: https://help.github.com/articles/creating-a-pull-request/
[django]: https://github.com/django/django/blob/master/CONTRIBUTING.rst
[gh actions build]: https://github.com/projectmesa/mesa/actions/workflows/build_lint.yml
[google style guide]: https://google.github.io/styleguide/pyguide.html
[license]: https://github.com/projectmesa/mesa/blob/main/LICENSE
[matrix]: https://matrix.to/#/#project-mesa:matrix.org`
[mesa discussions]: https://github.com/projectmesa/mesa/discussions
[pep8]: https://www.python.org/dev/peps/pep-0008
[pre-commit]: https://github.com/pre-commit/pre-commit
[tim pope's guideline]: https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
