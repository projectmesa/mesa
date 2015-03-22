# Project Mesa

[![Coverage Status](https://coveralls.io/repos/projectmesa/mesa/badge.svg)](https://coveralls.io/r/projectmesa/mesa)[![Coverage Status](https://coveralls.io/repos/projectmesa/mesa/badge.svg)](https://coveralls.io/r/projectmesa/mesa)

### Warning: work in progress!

Mesa is a new agent-based modeling framework being written in Python.

## Design Principles

**Minimal assumptions:** Mesa shouldn't assume that a model is built a certain way. Everything, from the agent activation schedule to whether or not the agents are 'spatial' should be easily specified in the code. However, that shouldn't mean that you need to code *everything* from scratch every time you want to write a new model. Which brings us to...

**Modularity:** Mesa is designed from the ground up to be as modular as possible. Our hope is to encourage the development of basic, reusable blocks which can be validated and then reused across multiple models.

**Separate the model from the visualization:** Sometimes you want to run a model carefully and examine it step by step. Other times you want to wow an audience with a smooth animated simulation. When you're ready to science with your model, you want to run it 100,000 times with different parameters and explore the results. The only way to reasonably do this is to separate out the visuals from the actual model.

**In-browser visualization:** GUIs are hard. Cross-platform GUIs are even harder. Nobody wants to deal with that. Everyone has a browser, and browsers (and the JavaScript that runs on them) work pretty much the same everywhere. So we're going to put the visualizations (and the visualizations only) in a web browser. However, users shouldn't have to write their own JavaScript to get a decent-looking visualization up and running. Our plan is to have a basic template, and a system which can populate it with a minimum amount of Python. If someone wants to customize their web visualization with their own fancy JS or CSS, it should be as easy as possible.

**Open-source:** Not just in theory, but in practice. We want this to be a community tool, built and updated to include the features that researchers actually want and use. Ideally, this can be a way of easily sharing both best-practices and cutting-edge methodologies.

**A pony:** You can have one. But you have to code it yourself. And share it with everyone.

## Setting up the virtual environment

Step -1.
* Install Python 3, if you don't have it yet.
* Install [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/)

Step 0.
* Create the virtual environment:
    * (If you have Python 3 only) mkvirtualenv mesa
    * (If you have both versions) mkvirtualenv mesa -p *path/to/python3*
        - On OSX or Linux, you can find the Python 3 path via *which python3*
* pip install -r requirements.txt
* add2virtualenv [path to ProjectMesa/mesa]

Step 1. - Using the environment
* workon mesa
* deactivate


