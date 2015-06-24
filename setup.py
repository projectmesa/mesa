#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

requires = [
    'tornado',
    'numpy',
    'pandas',
]

# TODO: Rewrite Readme and pull that it instead.
description = """
    Mesa is an agent-based modeling (or ABM) framework in Python. It allows
    users to quickly create agent-based models using built-in core components
    (such as spatial grids and agent schedulers) or customized
    implementations; visualize them using a browser-based interface; and
    analyze their results using Python's data analysis tools. It's goal is
    to be the Python 3-based alternative to NetLogo, Repast, or MASON.

    Mesa is being developed by a group of modeling practitioners with
    experience in academia, government, and the private sector.
"""

setup(
    name='Mesa',
    version='0.6.0',
    description=description,
    author='Project Mesa Team',
    author_email='projectmesa@googlegroups.com',
    url='https://github.com/projectmesa/mesa',
    packages=['mesa'],
    package_data={'': ['LICENSE.md', ], },
    package_dir={'mesa': 'mesa'},
    include_package_data=True,
    install_requires=requires,
    keywords='agent based modeling model ABM simulation multi-agent',
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Life',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
    ],
)
