import os
import sys
from pathlib import Path
from subprocess import call

import click

from mesa import __version__

PROJECT_PATH = click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True
)
COOKIECUTTER_DIR = "mesa/cookiecutter-mesa"
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIECUTTER_PATH = os.path.join(os.path.dirname(SCRIPTS_DIR), COOKIECUTTER_DIR)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    "Manage Mesa projects"


@cli.command()
@click.argument("project", type=PROJECT_PATH, default=".")
def runserver(project):
    """Run mesa project PROJECT

    PROJECT is the path to the directory containing `run.py`, or the current
    directory if not specified.
    """
    run_files = ["run.py", "server.py"]
    for run_file in run_files:
        run_path = Path(project) / run_file
        if not run_path.exists():
            continue
        args = [sys.executable, str(run_path)]
        call(args)
    sys.exit(f"ERROR: file run.py or server.py (in {Path(project)}) does not exist")


@click.command()
@click.option(
    "--no-input", is_flag=True, help="Do not prompt user for custom mesa model input."
)
def startproject(no_input):
    """Create a new mesa project"""
    args = ["cookiecutter", COOKIECUTTER_PATH]
    if no_input:
        args.append("--no-input")
    call(args)


@click.command()
def version():
    """Show the version of mesa"""
    print(f"mesa {__version__}")


cli.add_command(runserver)
cli.add_command(startproject)
cli.add_command(version)
