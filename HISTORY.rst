.. :changelog:

Release History
---------------

0.8.7 (2020-05-05) Mammoth
+++++++++++++++++++++++++++++++++++++++++++

**Improvements**

* Enable BatchRunner to run specified set of parameter combinations #651 (#607)
* Restructured runcontrol.js #661
* Add pipenv support for mesa #678
* Increase test coverage and change to codecov #692
* Updates Travis to explicitly set the dist to be Xenial #699
* time: Remove resolved TODO on random seed of random scheduler #708
* hex_snowflake: Update description to be more informative #712
* Added Coverall to Codecov in Contributing file #734
* Makes opening the browser optional when launching the server #755 #754
* NetworkGrid: Update to networkx 2.4 API #763
* Apply black to mesa/ directory #775
* Updated travis to 3.8 and updated gitignore #777
* Add information (to docstring) on image as agent portrayal shape #791
* Change grid empties from list to set #649 (improves speed)
* Adding mypy annotation
    * space: Add type annotation to Grid class #779
    * add Mypy annotation to time, agent, and model #792
    * space: Add mypy annotation to the remaining methods/functions #796
* Docs related
    * Bulk merge of docs from 'docs' to 'master' #684
    * Created useful snippets code section in the docs #668 #669
        * Updating index.rst #672
        * Clarify runserver snippet in index.rst #682
    * Add documentation for feature (pipenv) added in #678 #683
    * Add docs for BatchRunner to support Variable and Fixed Parameter Contribution #679 #683
        * Resources #651 in docs branch #691. This preps for #683 to be merged.
    * intro tutorial: Clarify a function that is not defined in the class #705
    * Updates formatting the readme Docs markdown #737
* Examples related
    * Schelling: Separate text-only viz into run_ascii.py #706
    * examples/Readme.md: Update description to be consistent with the folder names #707

**Fixes**

* Fixes link to update code coverage module - Updates Removing last link to coveralls and replacing to codecoverage #748
* Fixes D3 Network Visualization to update (rather than overwrite) #765 #767
* Fix parameter order in initializing SingleGrid object #770 #769
* Updating pipenv link #773
* Fixed pip install from github by specifying egg #802
* Compatibility fixes
    * Fixes VisualizationServer to be compatible with recent versions of Tornado #655
    * Fixes #749 networkx incompatibility #750
* Fixing typos
    * Fixes documentation typos in example code #695 #696
    * Fixes typo in ModularServer's last parameter #711
    * Fixed typo in BarChartModule line 100 #747
    * Fix typo in documentation #809
* Doc fixes (not relating to typos)
    * Update tutorial to point to correct repo location #671 #670
    * Updating sphinx and reverting issues #674 #675 #677 #681
    * Fixes code blocks that weren't showing up in the tutorial #686
    * Remove figure from advanced tutorial showing the empty visualization #729
    * Removes git clone from tutorial - Update intro_tutorial.rst #730
    * Fixes citation links in docs tutorial section #736
    * Fix histogram in advanced tutorial #794 #610
    * Fixes Advanced Tutorial #elements #804 #803
* Fixes to examples
    * Fixing test_random_walk bug - wolf sheep. #821
    * Fixes shape_example server launch #762 #756
    * Fixing broken table in pd_grid example #824



0.8.6 (2019-05-02) Lake Havasu City
+++++++++++++++++++++++++++++++++++++++++++

**Improvements**

* add docker-compose + Dockerfile support #593
* install: Remove jupyter requirement #614
* Add Bar and Pie Chart visualization #594 #490
* Make models pickleable #582


**Fixes**

* Year update. Happy New Year! #613
* Fixed problem with grid and chart visualization javascript #612 #615
* removed extra" .random" on line 178. #654
* updated requirement for networkx #644 #646
* Fix VisualizationServer to be compatible with recent versions of Tornado #655


0.8.5 (2018-11-26) Kearny
+++++++++++++++++++++++++++++++++++++++++++

**Improvements**

* Added mouse interactionHandler to close #457, fixed hexgrid drawLines #465
* Run examples as part of the tests #529, #564
* Add a github issue template. #560
* Changes nose to pytest #561
* Update and clean up cookiecutter layout #563
* Updating setup to move requirements to setup.py. #566
* Fixes #570 removed and updated stale comments in space.py #571
* Adding model random number generator with __new__ #572
* Faster agent attribute collection #576
* Update install command to be edible #578
* Adding read the docs yml. #579
* agents can be removed and added during Scheduler.step() #584
* Adding a description to bank_reserves. #587
* F8 cleanup #600

**Fixes**

* Fixes #543 (User Settable Parameters fail to work for non-string datatype #543) #544
* Adding missing requirements files to examples. #550
* Fixes issue #548, flockers visualization not showing up #548
* updated BatchRunner (throwing error when passing in agent reporters) #556
* Removing version numbers and fixing flake8 issues. #562
* Fix issue #548 (Flockers visualization is not working) #566
* Fixes code formatting in readmes. #577
* Batchrunner.fix (BatchRunner's "variable parameters" is not strictly optional) #596


0.8.4 (2018-06-17) Jerome
+++++++++++++++++++++++++++++++++++++++++++

**Improvements**

* Mesa Packages docs created (#464, #480, #484, #503, #504)
* Change size and tooltip text of nodes in D3 network visualization #468
* Multiprocessing BatchRunner with pathos #506
* Schedule.agent.dict - Implement tracking the agents in the scheduler via OrderedDict #510
* Use click and add `mesa run` #522
* Add a code of conduct #530

**Fixes**

* iter_neighborhood() now gives correct neighborhoods for both von Neumann and Moore #459
* fix typo #461
* Flockers update & subsequent "F" versus "f" fix on Unix/Mac - #477, #518, #525, #500
* Fixing date on release. #453
* Batchrunner fixes: properly initialize models with correct parameters during subsequent runs. #486
* Tornado Version Bug Fixes (upgrading #489, downgrading #497, adding to setup.py #527)
* fix minor flake8 issues #519
* align required dependencies between setup.py and requirements.txt #523, #528, #535
* Fixes #499 grid size issue. #539


0.8.3 (2018-01-14) Hayden
+++++++++++++++++++++++++++++++++++++++++++

**Improvements**

* Datacollector fix #445
* A first network grid model with visualization, using NetworkX and sigma.js #388
* Cache pip packages for Travis setup #427
* Remove localhost hardcoding + allow secure sockets #421
* Update Chart.js to version 2.7.1 #401
* Bank reserves example #432
* Extended Grid to support hexagonal grids #409

**Fixes**

* Faster ContinuousSpace neighbor search #439
* Updating license year to 2018 #450
* Updating language on license in contributing file #446
* Updating license year to 2018 #450
* Removed mutable defaults from DataCollector constructor #434
* [BUGFIX] Torus adjustment in Grid class #429
* Batchrunfixedparameters #423
* [BUGFIX] Fix sidebar visibility in Edge #436
* Updating Travis svg to target #master, not branches. #343
* Email list language updates and link updates #399
* Fix math problems in flockers; use numpy in space #378
* Only start tornado ioloop if necessary #339
* ContinuousSpace: Fix get_distance calculation on toroidal boundary condition #430


0.8.2 (2017-11-01) Gila Bend
+++++++++++++++++++++++++++++++++++++++++++

**Improvements**

* Split parameter_values into fixed & variable parameters in batchrunner #393

**Fixes**

* Updating License year to 2017 -- very minor update #391
* Flockers: fix param naming #398
* Remove unused class parameters. #400
* [hotfix!] Disable e2e viz test for now. #414
* Fixing bug in release process. [6a8ecb6]
    * See https://github.com/pypa/pypi-legacy/issues/670.


0.8.1 (2017-07-03) Flagstaff (PyCon Sprints & then some)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++

**Improvements**

* Bootstrap UI starter #383
* Add Sugarscape Constant Growback example #385
* Add best-practices document and describe models. #371
* Refactored & model standards related:
    * Prisoner's Dilemma refactor to meet new model standard format. #377
    * refactored boltzmann wealth model to new layout #376
    * Update tutorial to follow new model standards #370
    * Moving wolf sheep pngs to sub-folder for better organization #372
    * Add best-practices document and describe models. #371
* Modified loop over agents in schedule step method #356
* Added function to use local images as shapes in GridDraw #355

**Fixes**

* Fix math problems in flockers; use numpy in space #378
* Seed both global random number generators #373, #368
* Dictionary parameters fix #309
* Downgrade setuptools to fix #353
* Minor forest fire fix #338, #346
* Allow fixed seed for replication #107
* Fix tutorial and example readme for port change 8b57aa


0.8.0 (2017-01-29) - Edgar
+++++++++++++++++++++++++++

**Improvements**

* Updating contribution file to prevent future travis breaks #336
* Updating Travis svg to target #master, not branches. #343
* implement "end" message in visualization #346
* Move empty-cell functions to baseclass Grid #349

**Fixes**

* Only start tornado ioloop if necessary #339
* fix boundaries of ContinousSpace #345


0.7.8.1 (2016-11-02) Duncan
++++++++++++++++++++++++++++

**Improvements**

* Fixes #324 -- renames all examples to be the pythonic format of naming #328
* Changing to port 8521, fixes #320. #321
* Opens a browser window when launching the server #323
* Ticket #314 - added progress bar to BatchRunner #316
* Auto update year for copyright. #329

**Fixes**

* Minor bug fixes - Update ForestFire example notebook to new API, and rename Basic to Shape Example. #318
* On-demand model stepping rather than an endless buffer #310
* Updating contribution to prevent future travis breaks #330



0.7.7 (2016-08-18)
++++++++++++++++++

**Improvements**

* Fixes - variable name heading0/1 in ArrowHead shape is not intuitive. #295 #301
* Fixes - ArrowHead shape is not reflecting in the docs of api #300 #301
* Fixes - Documentation is not reflecting latest changes wrt width-height argument order in Grid() #296 #301


0.7.6 (2016-08-13)
++++++++++++++++++

Theme: Scipy Sprints 2016 ( ‘-’)人(ﾟ_ﾟ )
& Then some.

**Feature adds**

* Add new shapes & direction indication in CanvasGrid #285
* Provides support for text overlay on Circle and Rectangle shapes. #265

**Improvements**

* Fixes Parameters of CanvasGrid(): row, col, height, width inverted #285
* Fixes 'coordinates on grid are used inconsistently throughout the code' #285
* Moves Agent and Model class outside of  __init__.py #285
* Minor pep updates to boltzmann. #269
* Fix link to intro tutorial. #267
* Updating template text visualization/ModularVisualization.md #273
* Update intro_notebook and documents to include self.running = True in MoneyModel #275
* Update .rst file location to make sure ReadTheDocs works correctly #276
* Remove Mock code causing recursion and preventing build of docs. #281
* MultiGrid docstring missing methods #282
* No Docstring for model.grid.get_cell_list_contents #282
* Refactor forest fire example #223 #288
* Updating kernel version on forest fire model. #290
* Making examples pep complaint. fixes #270 #291
* Fixed pep8 examples and #292 #294
* Fixes #283 - Fixes formatting on viz readme #299
* Have Agent use self.model instead of passing it around #297


0.7.5 (2016-06-20)
++++++++++++++++++

**Pre-sprints**

* Update of tutorial files and docs #176, #172
* Adds np.int64() functions around some variables to get rid error caused by numpy update #188
* Made examples Readme.md more readable #189

**From PyCon Sprints**

* Updating model example readmes #207
* Added nose to requirements #208
* Updated link on style google style guide #209
* Reset visualization when websocket connection is opened #210
* Remove unused scipy dependency #211
* Introduce a requirements.txt for the tutorial. #212
* Remove references to running in tutorial #213
* Simplify travis.yml; add python versions #215
* Update Flocker Readme.md #216
* Syntax error in .rst was swallowing a code block #217
* Fixup HistogramModule in the tutorial. #218
* add more test coverage to time #221
* add a requirements.txt for WolfSheep. #222
* add a requirements.txt for Schelling. #224
* Refactor color patches example #227
* Ignored _build sphinx docs still in repo #228
* Intro Tut completely in ipynb #230
* pass optional port parameter to ModularServer.launch #231
* open vis immediately when running color patches #232
* Adds .DS_store to .gitignore #237
* Documentation Update #240
* Small fix for reading links #241
* Test batchrunner #243
* clean up TextVisualization #245
* Documentation Update #250
* Update Game of Life example to new format #253
* Update Flockers example to new format #254
* Update Epstein model to new layout #255
* Subclassing object is unnecessary in Python 3 #258

**Post PyCon Sprints**

* Adds a copy of jquery directly into the code. #261


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

**Improvements**

* Allow cell_list_content methods in Grids to accept single tuples in addition to lists


0.6.6 (2015-07-11)
++++++++++++++++++

Theme: Scipy Sprints ( ‘-’)人(ﾟ_ﾟ )

**Improvements**

* Standardizes the arguments passed to spatial functions to only tuples, not separate x and y coordinates. (Breaks backwards compatibility)


0.6.5.1 (2015-07-11)
++++++++++++++++++

Theme: Scipy Sprints ( ‘-’)人(ﾟ_ﾟ )

**Improvements**

* Adding version, license, copyright, title to __init__.py
* Auto updating version in setup.py

**Fixes**

* Updating MANIFEST.in to include visualization templates that were missing.


0.6.5 (2015-07-11)
++++++++++++++++++

Theme: Scipy Sprints ( ‘-’)人(ﾟ_ﾟ )

**Edits**

* Additions to tutorial doc
* Minor edits to README & Intro
* Minor edits / clean up to setup.py
* Removing .ipynb_checkpoints
* Removing out-of-date planning documentation.

**Fixes**

* Use setuptools' find_packages function to get the list of packages to install, fixes #141

**Improvements**

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

* Fixes: Order of operations reversed: agent is removed first and then it is placed.
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
