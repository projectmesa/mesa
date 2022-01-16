#!/usr/bin/env python
from setuptools import setup, find_packages

requires = ["mesa"]

setup(
    name="{{cookiecutter.snake}}",
    version="0.0.1",
    packages=find_packages(),
    install_requires=requires,
)
