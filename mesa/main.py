import os
import sys
from subprocess import call

import click

PROJECT_PATH = click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True
)
COOKIECUTTER_DIR = "mesa/cookiecutter-mesa"
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIECUTTER_PATH = os.path.join(os.path.dirname(SCRIPTS_DIR), COOKIECUTTER_DIR)


@click.group()
def cli():
    "Manage Mesa projects"


@cli.command()
@click.argument("project", type=PROJECT_PATH, default=".")
def runserver(project):
    """Run mesa project PROJECT

    PROJECT is the path to the directory containing `run.py`, or the current
    directory if not specified.
    """
    sys.path.insert(0, project)
    os.chdir(project)

    with open("run.py") as f:
        code = compile(f.read(), "run.py", "exec")
        exec(code, {}, {})  # noqa: S102


@click.command()
@click.option(
    "--no-input", is_flag=True, help="Do not prompt user for custom mesa model input."
)
def startproject(no_input):
    args = ["cookiecutter", COOKIECUTTER_PATH]
    if no_input:
        args.append("--no-input")
    call(args)


cli.add_command(runserver)
cli.add_command(startproject)
