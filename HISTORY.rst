.. :changelog:

Release History
---------------

Next release
++++++++++++++++++

* ???

0.7.0 (2016-03-06)
++++++++++++++++++
* #184 Adding terminal echo for server launch to signal person running the model
* #183 Adding Conway's Game of Life simulation to the examples.

0.6.9 (2016-02-16)
++++++++++++++++++

* #170 Adding multi-stage activation
* #169 Wolf-Sheep Cleanup
* Updates requirements to latest libraries


0.6.7 (2015-07-11)
++++++++++++++++++

* Improvements
    * Allow cell_list_content methods in Grids to accept single tuples in addition to lists


0.6.6 (2015-07-11)
++++++++++++++++++

Theme: Scipy Sprints ( ‘-’)人(ﾟ_ﾟ )

* Improvements
    * Standardizes the arguments passed to spatial functions to only tuples, not separate x and y coordinates. (Breaks backwards compatibility)


0.6.5.1 (2015-07-11)
++++++++++++++++++

Theme: Scipy Sprints ( ‘-’)人(ﾟ_ﾟ )

* Improvements
    * Adding version, license, copyright, title to __init__.py
    * Auto updating version in setup.py
* Bug fix
    * Updating MANIFEST.in to include visualization templates that were missing.


0.6.5 (2015-07-11)
++++++++++++++++++

Theme: Scipy Sprints ( ‘-’)人(ﾟ_ﾟ )

* Edits
    * Additions to tutorial doc
    * Minor edits to README & Intro
    * Minor edits / clean up to setup.py
    * Removing .ipynb_checkpoints
    * Removing out-of-date planning documentation.
* Bug fix
    * Use setuptools' find_packages function to get the list of packages to install, fixes #141
* Improvements
    * Use package_data for include the web files
    * Use a MANIFEST.in file to include the LICENSE file in source distributions
    * Using conda on Travis allows much faster builds and test runs


0.6.2 (2015-07-09)
++++++++++++++++++

* Improvement: Adding continuous space.
* Improvement: Adding a simultaneous activation scheduler.
* New models:
	- Flockers
	- Spatial Demographic Prisoner's Dilemma (PD_Grid)

0.6.1 (2015-06-27)
++++++++++++++++++

* Bug Fix: Order of operations reversed: agent is removed first and then it is placed.
* Improvement: `LICENSE`_ was updates from MIT to Apache 2.0.

.. _`LICENSE` : https://github.com/projectmesa/mesa/blob/master/LICENSE


0.6.0 (2015-06-21)
++++++++++++++++++

* Improvment: Add modular server feature, which breaks up a model into a .py file and a .js file. This breaks backwards compatibility.

Pre 0.6.0
++++++++++++++++++

Code that is pre-0.6.0 is very unstable.

Our inital release was 0.5.0 (2014-11).

It included code for placing agents on a grid; a data collector and batch runner; and a front-end visualization using HTML 5 and JavaScript.

**General**

* Objects create -- Agent, Time, Space
* Project moved to Python 3
* Tornado server setup

**Front-end**

* Front-end grid implemented
* ASCII visualization implemented

**Examples models**

* Forest Fire
* Schelling
* Wolf-Sheep Predation

**0.1.0 (2014-09-19)**

* A conversation
* Birth
