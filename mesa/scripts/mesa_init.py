#!/usr/bin/env python

"""
Scaffolding command to build a new mesa project
"""

import os
from subprocess import call


COOKIECUTTER_DIR = 'cookiecutter-mesa'
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIECUTTER_PATH = os.path.join(os.path.dirname(SCRIPTS_DIR), COOKIECUTTER_DIR)


def main():
    print(COOKIECUTTER_PATH)
    print(type(COOKIECUTTER_PATH))
    call(['cookiecutter', COOKIECUTTER_PATH])

if __name__ == '__main__':
    main()
