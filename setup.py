#!/usr/bin/env python
import re
from codecs import open

from setuptools import find_packages, setup

requires = [
    "click",
    "cookiecutter",
    "matplotlib",
    "mesa_viz_tornado~=0.1.0,>=0.1.2",
    "networkx",
    "numpy",
    "pandas",
    "solara",
    "tqdm",
]

extras_require = {
    "dev": [
        "black",
        "ruff~=0.1.1",  # Update periodically
        "coverage",
        "pytest >= 4.6",
        "pytest-cov",
        "sphinx",
    ],
    # Explicitly install ipykernel for Python 3.8.
    # See https://stackoverflow.com/questions/28831854/how-do-i-add-python3-kernel-to-jupyter-ipython
    # Could be removed in the future
    "docs": [
        "sphinx",
        "ipython",
        "ipykernel",
        "pydata_sphinx_theme",
        "seaborn",
        "myst-nb",
    ],
}

version = ""
with open("mesa/__init__.py") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

with open("README.rst", "rb", encoding="utf-8") as f:
    readme = f.read()


setup(
    name="Mesa",
    version=version,
    description="Agent-based modeling (ABM) in Python 3+",
    long_description=readme,
    author="Project Mesa Team",
    author_email="projectmesa@googlegroups.com",
    url="https://github.com/projectmesa/mesa",
    packages=find_packages(),
    package_data={
        "cookiecutter-mesa": ["cookiecutter-mesa/*"],
    },
    include_package_data=True,
    install_requires=requires,
    extras_require=extras_require,
    keywords="agent based modeling model ABM simulation multi-agent",
    license="Apache 2.0",
    zip_safe=False,
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Life",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
    ],
    entry_points="""
        [console_scripts]
        mesa=mesa.main:cli
    """,
    python_requires=">=3.8",
)
