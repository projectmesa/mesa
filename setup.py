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
# First, ensure that the external/ directory exists
os.makedirs(external_dir, exist_ok=True)


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


# Important: when you update JS dependency version, make sure to also update the
# hardcoded included files and versions in: mesa/visualization/templates/modular_template.html

# Ensure Bootstrap
bootstrap_version = "3.3.7"
ensure_JS_dep(
    f"bootstrap-{bootstrap_version}-dist",
    f"https://github.com/twbs/bootstrap/releases/download/v{bootstrap_version}/bootstrap-{bootstrap_version}-dist.zip",
)

# Ensure Bootstrap Slider
bootstrap_slider_version = "9.8.0"
ensure_JS_dep(
    f"bootstrap-slider-{bootstrap_slider_version}",
    f"https://github.com/seiyria/bootstrap-slider/archive/refs/tags/v{bootstrap_slider_version}.zip",
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
