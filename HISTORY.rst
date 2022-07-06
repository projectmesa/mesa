.. :changelog:

Release History
---------------

1.0.0 (2022-07-06) Quartzsite
+++++++++++++++++++++++++++++++++++++++++++

**Special notes**

* BREAKING: Rename mesa.visualizations.TextVisualization.TextElement to ASCIIElement
* POTENTIALLY BREAKING: Default batch_run to 1 CPU #1300 
* Simplified namespace implements - see Improvements section.

**Improvements**

* Implement simplified namespace
    * docs: simplified namespace tutorial update #1361 
    * examples: Convert shape_example, sugarscape_cg, virus_on_network, wolf_sheep to simple namespace #1339 
    * Convert hex_snowflake, pd_grid, schelling to simple namespace; [BREAKING] Remove class name collision #1333 
    * examples: Convert color_patches, conways_game_of_life, epstein_civil_violence, forest_fire to simple namespace #1331 
    * Examples: Convert boltzmann_wealth_model_network and chart to simple namespace #1322 
    * examples: Convert boid_flockers, boltzmann_wealth_model to simple namespace #1321
    * examples: Convert bank_reserves to simple namespace #1317
    * add batch_run to simple namespace #1316 
    * Implement simpler Mesa namespace #1294

* mypy 
    * mypy: Use "|" operator instead of Union/Optional #1345
    * mypy: Improve space.py annotation, part 2 #1219 
    * mypy: Improve annotations #1212 

* Userparam class updates
    * feat: Implement NumberInput UserParam class #1343 
    * feat: Implement StaticText UserParam #1342 
    * feat: Implement Choice UserParam class #1338 
    * feat: Implement Checkbox UserParam class #1332 
    * feat: Implement Slider UserParam class #1272
        * examples: Convert to using Slider UserParam class #1340 

* Front-end updates
    * frontend: Add alignment options to agent portrayals in CanvasGridVisualization #1349
    * frontend: Update Bootstrap 4.6.1 -> 5.1.3 #1325
    * ChartModule.js: Use more semantic HTML element creation method #1319 
    * Issue #1232; Replaced usage of var to const/let in some files #1248 
    * [Issue 1232] Refactor NetworkModuleSigma PieChartModule TextModule JS #1246
    * js: Update D3 from 4.13.0 to 7.4.3 #1270 
    * support package and local css includes #1283 
    * Upgrade to Bootstrap 4! #1282
    * refactor: update var to const/let in InteractionHandler.js #1273 
    * Change remaining vendored JS dependencies to be downloaded during install #1268 
    * Download jQuery and D3 during install #1260
    * CSS support for custom visualization element #1267 
    * style: prettify js files #1266 
    * refactor: Change var to const/let for remaining js files #1265 
    * Remove NetworkModule_sigma and its dependencies #1262 
    * js: Download bootstrap-slider during install #1257 
    * js deps: Move Bootstrap to be inside external folder #1236 
    * Apply prettier to NetworkModule_d3.js #1225 
    * js: Download Bootstrap on-the-fly during install instead #1220 
    * Install JS dependencies using Fanstatic #1195 
    * JQuery updates
        * examples: Remove all usage of jQuery #1356
        * Remove jQuery dependency completely #1355
        * refactor: frontend: Remove remaining usage of jQuery #1351 
        * refactor: frontend: Remove usage of jQuery for most of the JS code #1348 
        * refactor: frontend: Remove jQuery usage in CanvasHexModule.js & CanvasModule.js #1347 
        * refactor: frontend: Remove jQuery usage in BarChartModule.js #1326 
        * visualization: Specify tooltip without jQuery #1308

* CI Updates
    * ci: Ensure wheel is install before pip install step #1312
    * Fix contributing (increasing black version) #1303
    * ci: Disable PyPy for now #1254 
    * CI: Update checkout, setup-python and cache actions to v3 #1217 
    * CI: Split off codespell job, don't run build on doc changes #1170 
    * ci: Add 6 min timeout for the test jobs #1194 
    * CI: test flake: batch runner sometimes takes 6 hours then gets killed by GitHub Actions #1166 
    * ci: Enable cache for all Python versions 🇺🇦 #1177 
    * CI: Create Action to publish to PyPI on release #1169 
    * CI: Python 3.6 should be removed because it has reached EOL #1165
    * Update Black formatting (no spaces for power operator) #1160
    * Improve code quality with static analysis #1328 
    * CI test: Increase timeout to 10 minutes #1250 

* Dependency updates 
    * build(deps): bump cookiecutter from 2.1.0 to 2.1.1 dependencies #1360
    * Update Pipfile.lock (dependencies) #1350, #1301, #1224, #1203, #1135 by github-actions bot 
    * Migrate D3 from v4 to v7 #1088 

* Other Improvements
    * feat: Implement auto-conversion of function to TextElement #1346 
    * Readme: Add Matrix badge and description #1164
    * examples: Convert nodes to list when drawing random sample#1330
    * examples: Use nicer color for bank_reserves #1324 
    * examples: Use nicer color for chart #1323 
    * model: Implement initialize_data_collector #1287
    * CONTRIBUTING: Add instruction to enable git pull autorebase #1298 
    * Improve MANIFEST.in #1281 
    * refactor: Merge _remove_agent into remove_agent #1245 
    * examples: Remove usage of internal method _remove_agent #1241 
    * refactor: Make _place_agent args consistent with place_agent #1240 
    * Redirect user to GH discussions for seeking help #1237 
    * setup.py: Update setup classifiers and add python_requires for Python>=3.7 #1215 
    * The tutorial.rst doesn't mention that the Pandas DataFrame output can be in CSV #1148 
    * Deprecate neighbor_iter in favor of iter_neighbors #1184 
    * Add snippet about using numpy's random #1204 
    * docs: make windows multiprocessing code appear #1201 
    * Capitalize CSV whenever applicable #1200 
    * update intro tutorial for pandas and CSV and batch_run and windows #1196 
    * docker-compose.yml: Make it consistent with Dockerfile #1197 
    * Improve Dockerfile #1193 
    * update to include Matrix and GitHub discussion links #1179 
    * Update docs to remove old discussion forums #1171 
    * Add "Grass" curve to wolf_sheep example chart #1178 
    * feat: Implement random activation by type #1162 


**Fixes**

* Git tags out of sync with conda and PyPi (0.8.8 and 0.8.9 missing on git) #1076
* fix: Remove mesa.visualization.Number #1352
* CI: the "install dependencies" step is slow #1163 
* Readme related
    * readme: Clarify/Update Docker instruction #1222, #1214
    * Readme: Fix links to docs #1205 
* Add mesa/visualization/templates/js/external to gitignore #1320
* fix: sugarscape_cg: Use better way to check if a cell is occupied by SsAgent #1313 
* fix double multiply of iterations in singleprocess #1310 
* pre-commit: fix required python version, correct example commit messa… #1302 
* fix: Make bank_reserves batch_run example work #1293 
* Fixes #498. Replaces canvas_width with grid_rows to fill out color patches  3 - Accept easy task!!! #989 
* update pre-commit to include jupyter; fix warning #1190 
* fix: Grid.__getitem__: Handle Numpy integers #1181 
* fix: Make argument order in example models consistent #1176 
* issue template: Linkify discussions url #1239 
* batch_run: Do not iterate values when it is a single string #1289 
* examples: Clarify install instruction in wolf_sheep #1275 
* test: Disable batchrunnerMP (CI: test flake: batch runner sometimes takes 6 hours then gets killed by GitHub Actions #1166) #1256 
* examples: correcting comment in examples/pd_grid/pd_grid/agent.py #1247 
* space: Clarify the return object of get_cell_list_contents #1242 
* width and height were changed up #1149 



0.9.0 (2022-01-31) Page
+++++++++++++++++++++++++++++++++++++++++++

**Improvements**

* Update number_processes and associated docs #1141
* [PERF] Improve move_to_empty performance #1116 
* Adding logic to check whether there is agent data #1115 
* Convert all text strings to f-strings #1099 
* Format Python and Jupyter Notebook files with Black #1078
* README: Add info on how to cite Mesa #1046 
* Re-Implementation of BatchRunner #924 
* CI Related
    * CI: Add workflow to update Pipfile.lock every month #1018
    * CI: Lint typos with Codespell #1098 
    * CI: Only run Codecov on Ubuntu jobs and update to v2 #1083 
    * CI: Maintenance: Update to Python 3.10, split of lint jobs #1074 
* Dependency updates
    * Updates to Pipfile.lock (dependencies) #1114, #1086, #1080
    * Update Pipfile to use Python 3.9 #1075 
    * Update Chart.js to 3.6.1 (v3) #1087 
    * Update Chart.js to version 2.9.4 #1084
    * Pyupgrade 3.6: Update syntax with Python 3.6+ features #1105 
    * Bump urllib3 from 1.26.2 to 1.26.5 #1043 
    * Update packages.rst #1068 
* Docs
    * Update docs/README.md #1118 
    * Update number_processes and associated docs #1141
    * Update section 'Batch Run' of introductory tutorial #1119 
    * Readme: Add command to install specific branch #1111 
    * Docs: Add back some comments in space.py #1091 
    * Docs: Remove trailing white spaces #1106
    * Update intro_tutorial.rst #1097, #1095
    * Tweaking and improving the documentation #1072 

**Fixes**

* Rename i_steps -> data_collection_period and add docstring #1120 
* bank_reserves: Say that the commented out legacy code is for comparison #1110
* Fix broken image on PyPI #1071
* Docs
    * Fix numbering typos in docs/README.md #1117    
    * Readme: Fix command for installing custom branch on fork #1144 
    * Docs: space.py: Fix single case of neighbor spelled as neighbour #1090 


0.8.9 (2020-05-24) Oro Valley
+++++++++++++++++++++++++++++++++++++++++++

*Note: Master branch was renamed to Main on 03/13/2021*

**Improvements**

* Master to Main change:
    * Docs/examples: Update links to use main instead of master as branch #1012
    * CI: Run on pushed to main and release branches #1011
* Github Actions
    * GitHub Actions: run black only on ubuntu 3.8 #996
    * GA: Only run CI when pushed to master #974
    * GA: Add pypy3 #972
    * rename github action to "build", remove redundant flake8 check #971
    * GA: Run on Windows and macOS #970
    * Add GitHub Action for continuous integration testing #966
* [PERF] Add neighborhood cache to grids and improve iter_cell_list_contents #823
* forest_fire: Remove unnecessary code #981
* Migrate away from type comments #984
* Update License #985
* Public remove_agent function for NetworkGrid #1001
* Date update to release #962
* Advanced indexing of grid #820

**Fixes**

* Correct spelling #999
* Update Pipfile.lock #983
* Fix order of variable_params in model and agent vars data frames #979
* Fix asyncio on windows with python 3.6 #973


0.8.8 (2020-11-27) Nogales
+++++++++++++++++++++++++++++++++++++++++++

*Note: This is the last version to support Python 3.5.*

**Improvements**

* Added pre-commit to automatically maintain a standard formatting with black #732

**Fixes**

* MultiGrid: Set to using list for cell content #783
* Docs
    * Fixed broken link to templates list in advanced tutorial. #833
    * Fixed image links in rst #838
    * Cleaned html to attempt correct build #839
    * Fixed links on Boltzmann model #843
    * Documentation update - batchrunner & data collector #870
    * Deleted readthedocs.yml #946
    * Doc builds #837, #840, #844, #941, #942
* Fixed bulleted list in contribution read me #836
* Updated test_examples.py, changed unused generator expression to actually run the models. #829
* Fixed #827 issue (example Epstein Civil Violence Jupyter Notebook typos) #828
* Eliminated Ipython3 references #841
* Fixed cookie cutter Fixes #850. #853
* Removed relative imports -- fix #855. #863
* Updated pytest requirement to fix issues on travis #864
* Made linux compatible - travis #886
* Fixed python 3.5 fails, boid failure #889, #898
* Travis: Removed python 3.5 #899
* Fixed example testing issues close multiprocess pools #890
* Used ordered dict to make compatible with python 3.5 #892
* Increased number of test to fix codecov patch #916
* Fixed for #919, adding an exception for duplicate ids. #920
* Batchrunner
    * Batch runner redux #917
    * Fixed empty/None `variable_parameters` argument to BatchRunner (#861) #862
    * Added ordereddict to BatchrunerMP for python 3.5 #893
    * Fixed python 3.5 fails bathrunnerMP (multiple tries) #897, #896, #895
    * Batchrunner_redux fixes #928
* Fixed variables names, mp function locations, datacollector #933
* ModularServer updated: Fix EventLoop and changes to default port #936
* Ran black 20.8b1, which formats docstrings #951



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

.. _`LICENSE` : https://github.com/projectmesa/mesa/blob/main/LICENSE


0.6.0 (2015-06-21)
++++++++++++++++++

* Improvement: Add modular server feature, which breaks up a model into a .py file and a .js file. This breaks backwards compatibility.

Pre 0.6.0
++++++++++++++++++

Code that is pre-0.6.0 is very unstable.

Our initial release was 0.5.0 (2014-11).

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
