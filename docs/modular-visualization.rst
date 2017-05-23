Modular Visualization - An In-Depth Look
========================================

Modular visualization is one of Mesa's core features. Mesa is designed
to provide predefined visualization modules, which can be easily
subclassed for your needs, and mixed-and-matched to visualize your
particular model. (Some day, Mesa hopes to host a wide variety.) This
document describes how to use and create new visualization modules.

Overview
--------

An interactive modular visualization is a set of **Elements**, each of
which is an instance of a visualization **Module**. To visualize a
model, create a new ModularServer with a list of the elements you want
to visualize, in the order you want them to appear on the visualization
web page.

For example, if you have a model ``MyModel``, and two elements,
*canvas\_vis* and *graph\_vis*, you would create a visualization with
them via:

.. code:: python

        server = ModularServer(MyModel, [canvas_vis, graph_vis])
        server.launch()

Then you will be able to view the elements in your browser at
http://127.0.0.1:8521/. If you prefer a different port, for example
8887, you can pass it to the server as an argument.

.. code:: python

        server.launch(8887)

Under the hood, each visualization module consists of two parts:

1. **Data rending** - Python code which can take a model object and
   renders it into some data describing the visualization.
2. **Browser rendering** - JavaScript object which in turn receives data
   from the Python render (via the ModularServer) and actually draws it
   in the browser.

Using Pre-Built Modules
-----------------------

Mesa already comes with some pre-built modules. Using the built-ins
allow you to build a visualization without worrying about the HTML and
javascript. Consult the documention for a variety of modules.

One built-in module is **CanvasGrid**, which you can use to visualize
objects located on grid cells. The CanvasGrid will cover a majority of
agent-based models, particularly the simpler ones.

CanvasGrid iterates over every object in every cell of your model's grid
(it assumes that your model has a grid named **grid**) and converts it
into a dictionary which defines how it will be drawn. It does this via a
**portrayal\_method**: a function which the user defines, which takes an
object as an input and outputs a dictionary with the following keys:

::

    "Shape": Can be "circle", "rect" or "arrowHead"
        For Circles:
            "r": The radius, defined as a fraction of cell size. r=1 will fill the entire cell.
        For rectangles:
            "w", "h": The width and height of the rectangle, which are in fractions of cell width and height.
        For arrowHead:
            "scale": Proportion scaling as a fraction of cell size.
            "heading_x": represents x direction unit vector.
            "heading_y": represents y direction unit vector.
    "Color": The color to draw the shape in; needs to be a valid HTML color, e.g."Red" or "#AA08F8"
    "Filled": either "true" or "false", and determines whether the shape is filled or not.
    "Layer": Layer number of 0 or above; higher-numbered layers are drawn above lower-numbered layers.
    "text": Text to overlay on top of the shape. Normally, agent's unique_id is used .
    "text_color": Color of the text overlay.
    (Shapes also have "x" and "y" coordinates, for the x and y of the grid cell in which it is, but CanvasGrid adds those automatically).

For example, suppose for a Schelling model, we want to draw all agents
as circles; red ones for the majority (agent type=0), and blue ones for
the minority (agent type=1). The function to do this might look like
this:

.. code:: python

        def schelling_draw(agent):
            if agent is None:
                return
            portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}
            if agent.type == 0:
                portrayal["Color"] = "Red"
            else:
                portrayal["Color"] = "Blue"
            return portrayal

In addition, a CanvasGrid needs to know the width and height of the grid
(in number of cells), and the width and height in pixels of the grid to
draw in the browser.

To continue our Schelling example: suppose we have a Schelling model
with a grid of 10x10, which we want to draw at 500px X 500px. using the
portrayal function we wrote above, we would instantiate our
visualization element as follows:

.. code:: python

        canvas_element = CanvasGrid(schelling_draw, 10, 10, 500, 500)

Then, to launch a server with this grid as the only visualization
element:

.. code:: python

        server = ModularServer(SchellingModel, [canvas_element], "Schelling")
        server.launch()

Sub-Classing Modules
--------------------

In some cases, you may want to customize the internals of an existing
visualization module. The best way to do this is to create a subclass of
it.

For example, the TextElement module provides an HTML template to render
raw text, but nothing else. To use it, we need to create our own
subclass, which implements a **render** method to get
visualization-ready data (in this case, just a text string) out of a
model object.

Suppose we want a module which can get an arbitrary variable out of a
model, and display its name and value. Let's create a new subclass:

.. code:: python

        from mesa.visualization.ModularTextVisualization import TextElement

        class AttributeElement(TextElement):
            def __init__(self, attr_name):
                '''
                Create a new text attribute element.

                Args:
                    attr_name: The name of the attribute to extract from the model.

                Example return: "happy: 10"
                '''
                self.attr_name = attr_name

            def render(self, model):
                val = getattr(model, self.attr_name)
                return attr_name + ": " + str(val)

Now, if we wanted to use our new AttributeElement to add the number of
happy agents to our Schelling visualization, it might look something
like this:

.. code:: python

        happy_element = AttributeElement("happy")
        server = ModularServer(SchellingModel, [canvas_element, happy_element], "Schelling")
        server.launch()

Note that, in this case, we only wanted to change the Python-side render
method. We're still using the parent module's HTML and JavaScript
template.

Creating a new browser display
------------------------------

But what if we want more than just a different Python renderer; we want
to substantially change how a module displays in the browser, or create
a completely new module? To do this, we need to open up the JavaScript
as well:

Let's take a look at the internals of **TextModule.js**, the JavaScript
for the TextVisualization. Here it is, in all its glory:

.. code:: javascript

        var TextModule = function() {
            var tag = "<p></p>";
            var text = $(tag)[0];
            $("body").append(text);

            this.render = function(data) {
                $(text).html(data);
            };

            this.reset = function() {
                $(text).html("");
            };
        };

This code is the JavaScript equivalent of defining a class. When
instantiated, a TextModule object will create a new paragraph tag and
append it to the parent HTML page's *body*. The object will have two
methods attached:

1. *render(data)* -- uses JQuery to replace the HTML contents of the
   paragraph with the text it gets as an input. This function will be
   called at each step of the model, to draw the data associated with
   the model coming over the websocket.
2. *reset* -- replaces the contents of the div with a blank. This
   function will be called when the user presses the Reset button.

Now let's take a look at the TextModule's Python counterpart,
**TextElement** (which resides in **TextVisualization.py**). Again,
here's the whole thing:

.. code:: python

        from mesa.visualization.ModularVisualization import VisualizationElement

        class TextElement(VisualizationElement):
            js_includes = ["TextModule.js"]
            js_code = "elements.push(new TextModule());"

That's it! Notice that it is lacking a *render()* method, like the one
we defined above. Look at what is there: *js\_includes* is a list of
JavaScript files to import into the page when this element is present.
In this case, it just imports **TextModule.js**.

Next, *js\_code* is some JavaScript code, in Python string form, to run
when the visualization page loads. In this case, *new TextModule()*
creates a new TextModule object as defined above (which, remember, also
appends a new paragraph to the page body) which is then appended to the
array *elements*, that stores all the visualization elements currently
on the page.

To help understand why it looks like this, here's a snippet of
JavaScript from the overall visualization template itself, on how to
handle incoming data:

.. code:: javascript

        data = msg["data"]
        for (var i in elements) {
            elements[i].render(data[i]);
        }

Data to visualize arrive over the websocket as a list. For each index of
the list, the code passes that element of the data to the *render*
function of the corresponding element, in the elements array.

Currently, module JavaScript files live in the
*mesa/visualization/templates* directory, and the Python files live in
*mesa/visualization/modules*.

When creating a new module, the Python and JavaScript code need to be
written in synch: the module Python-side **render** method needs to
output data in the exact same format that the JavaScript **render**
function receives as an input.
