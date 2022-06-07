#!/usr/bin/env python
import re
import os
import urllib.request
import zipfile
import shutil

from setuptools import setup, find_packages
from codecs import open

requires = ["click", "cookiecutter", "networkx", "numpy", "pandas", "tornado", "tqdm"]

extras_require = {
    "dev": ["black", "coverage", "flake8", "pytest >= 4.6", "pytest-cov", "sphinx"],
    "docs": ["sphinx", "ipython"],
}

version = ""
with open("mesa/__init__.py") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

with open("README.rst", "rb", encoding="utf-8") as f:
    readme = f.read()

# Ensure JS dependencies are downloaded
external_dir = "mesa/visualization/templates/external"
# We use a different path for single-file JS because some of them are loaded
# the same way as Mesa JS files
external_dir_single = "mesa/visualization/templates/js/external"
# First, ensure that the external directories exists
os.makedirs(external_dir, exist_ok=True)
os.makedirs(external_dir_single, exist_ok=True)


def ensure_JS_dep(dirname, url):
    dst_path = os.path.join(external_dir, dirname)
    if os.path.isdir(dst_path):
        # Do nothing if already downloaded
        return
    print(f"Downloading the {dirname} dependency from the internet...")
    zip_file = dirname + ".zip"
    urllib.request.urlretrieve(url, zip_file)
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall()
    shutil.move(dirname, dst_path)
    # Cleanup
    os.remove(zip_file)
    print("Done")


def ensure_JS_dep_single(url, out_name=None):
    # Used for downloading e.g. D3.js single file
    if out_name is None:
        out_name = url.split("/")[-1]
    dst_path = os.path.join(external_dir_single, out_name)
    if os.path.isfile(dst_path):
        return
    print(f"Downloading the {out_name} dependency from the internet...")
    urllib.request.urlretrieve(url, out_name)
    shutil.move(out_name, dst_path)


# Important: when you update JS dependency version, make sure to also update the
# hardcoded included files and versions in: mesa/visualization/templates/modular_template.html

# Ensure Bootstrap
bootstrap_version = "5.1.3"
ensure_JS_dep(
    f"bootstrap-{bootstrap_version}-dist",
    f"https://github.com/twbs/bootstrap/releases/download/v{bootstrap_version}/bootstrap-{bootstrap_version}-dist.zip",
)

# Ensure Bootstrap Slider
bootstrap_slider_version = "11.0.2"
ensure_JS_dep(
    f"bootstrap-slider-{bootstrap_slider_version}",
    f"https://github.com/seiyria/bootstrap-slider/archive/refs/tags/v{bootstrap_slider_version}.zip",
)

# Important: when updating the D3 version, make sure to update the constant
# D3_JS_FILE in mesa/visualization/ModularVisualization.py.
d3_version = "7.4.3"
ensure_JS_dep_single(
    f"https://cdnjs.cloudflare.com/ajax/libs/d3/{d3_version}/d3.min.js",
    out_name=f"d3-{d3_version}.min.js",
)
# Important: Make sure to update CHART_JS_FILE in
# mesa/visualization/ModularVisualization.py.
chartjs_version = "3.6.1"
ensure_JS_dep_single(
    f"https://cdn.jsdelivr.net/npm/chart.js@{chartjs_version}/dist/chart.min.js",
    out_name=f"chart-{chartjs_version}.min.js",
)


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
        "mesa": [
            "visualization/templates/*.html",
            "visualization/templates/css/*",
            "visualization/templates/js/*",
            "visualization/templates/external/**/*",
        ],
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
        "Programming Language :: Python :: 3.7",
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
    python_requires=">=3.7",
)
