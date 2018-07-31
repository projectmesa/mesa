import sys
import os
import click
import importlib_resources
from shutil import copytree
from subprocess import call

PROJECT_PATH = click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True)
COOKIECUTTER_DIR = 'mesa/cookiecutter-mesa'
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIECUTTER_PATH = os.path.join(os.path.dirname(SCRIPTS_DIR),
                                 COOKIECUTTER_DIR)


@click.group()
def cli():
    'Manage Mesa projects'
    pass


@cli.command()
@click.argument('project', type=PROJECT_PATH, default='.')
def runserver(project):
    '''Run mesa project PROJECT

    PROJECT is the path to the directory containing `run.py`, or the current
    directory if not specified.
    '''
    sys.path.insert(0, project)
    os.chdir(project)

    with open("run.py") as f:
        code = compile(f.read(), "run.py", 'exec')
        exec(code, {}, {})


@click.command()
@click.option('--no-input', is_flag=True,
              help='Do not prompt user for custom mesa model input.')
def startproject(no_input):
    args = ['cookiecutter', COOKIECUTTER_PATH]
    if no_input:
        args.append('--no-input')
    call(args)


@click.command()
@click.option('--copy', is_flag=True, default=True,
              help='Copy example MODEL to current directory')
@click.option('--run', is_flag=True, default=False,
              help='Run example MODEL')
@click.option('--copyall', is_flag=True, default=False,
              help='Copy all examples into current folder.')
@click.argument('model', default='')
@click.pass_context
def examples(ctx, copy, run, copyall, model):
    """Copy or run a mesa example MODEL.

    Run without MODEL to list availabe example models"""
    if copyall:
        with importlib_resources.path('mesa', 'examples') as ex:
            copytree(ex, "examples")
    elif not model:
        click.echo('Available example models:')
        examples = importlib_resources.contents('mesa.examples')
        for model in examples:
            if not model.startswith('__') and not model.endswith('.md'):
                click.echo(model)
        click.echo("Use 'mesa examples MODEL --run' to start an example.")
    elif run:
        with importlib_resources.path('mesa.examples', model) as path:
            sys.path.insert(0, path)
            os.chdir(path)
            ctx.invoke(runserver)
    elif copy:
        with importlib_resources.path('mesa.examples', model) as ex:
            copytree(ex, model)


cli.add_command(runserver)
cli.add_command(startproject)
cli.add_command(examples)
