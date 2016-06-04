#!/usr/bin/env python

"""
Scaffolding command to build a new mesa project
"""

import os
import click
from subprocess import call


COOKIECUTTER_DIR = 'cookiecutter-mesa'
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIECUTTER_PATH = os.path.join(os.path.dirname(SCRIPTS_DIR),
                                 COOKIECUTTER_DIR)


@click.command()
@click.option('--no-input', is_flag=True,
              help='Do not prompt user for custom mesa model input.')
def main(no_input):
    args = ['cookiecutter', COOKIECUTTER_PATH]
    if no_input:
        args.append('--no-input')

    # subprocess call takes a list of args
    call(args)

if __name__ == '__main__':
    main()
