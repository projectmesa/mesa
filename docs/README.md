Docs for Mesa
=============

The readable version of the docs is hosted at [mesa.readthedocs.org](http://mesa.readthedocs.org/).

This folder contains the docs that build the docs for the core mesa code on readthdocs.

### How to publish updates to the docs

Updating docs can be confusing. Here are the basic setups.

#### Create the rST files from ipynb files
1. Change to the appropriate directory (usually docs/tutorials)
  * ```cd tutorials```
2. Create rST files using nbconvert
  * ```jupyter nbconvert --to rST *.ipynb```
  * **Requires**
    * jupyter: `pip install jupyter`
    * [pandoc](http://pandoc.org/installing.html)

##### Submit a pull request with updates
1. Create branch (either via branching or fork of repo) -- try to use a descriptive name.
 * ```git checkout -b doc-updates```
2. Update the docs. Save.
3. Build the docs, from the inside of the docs folder.
 * **Requires** sphinx: `pip install sphinx`
 * ```make html```
4. Commit the changes. If there are new files, you will have to explicit add them.
 * ```git commit -am "Updating docs."```
5. Push the branch
 * ```git push origin doc-updates```
6. From here you will want to submit a pull request to main.

##### Update read the docs

From this point, you will need to find someone that has access to readthedocs. Currently, that is [@jackiekazil](https://github.com/jackiekazil) and [@dmasad](https://github.com/dmasad).

1. Accept the pull request into main.
2. Log into readthedocs and launch a new build -- builds take about 10 minutes or so.

### Helpful Sphnix tips
* Build html from docs:
 * ```make html```
* Autogenerate / update sphninx from docstrings (replace your name as the author:
 * ```sphinx-apidoc -A "Jackie Kazil" -F -o docs mesa/```
