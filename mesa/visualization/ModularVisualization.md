Modular Visualization - An In-Depth Look
=================================================================

Modular visualization is (well, will be) one of Mesa's core features. Mesa does (will) include a wide range of predefined visualization modules, which can be easily subclassed for your needs, and mixed-and-matched to visualize your particular model. It should also be fairly straightforward to create new visualization modules. In this document, I will attempt to provide an overview of how to do both.

## Overview

An interactive modular visualization is a set of **Elements**, each of which is an instance of a visualization **Module**. To visualize a model, create a new ModularServer with a list of the elements you want to visualize, in the order you want them to appear on the visualization web page. 

For example, if you have a model MyModel, and two elements, *canvas_vis* and *graph_vis*, you would create a visualization with them via:
    
    server = ModularServer(MyModel, [canvas_vis, graph_vis])
    server.launch()

And then open your browser to http://127.0.0.1:8888/ in order to open it.

Under the hood, each visualization module consists of two parts: Python code which can take a model object and renders it into some data describing the visualization, and an HTML / JavaScript template which in turn receives data from the Python render (via the ModularServer) and actually draws it in the browser. 

Phew.

Okay, so what do you actually need to know?

## Using Pre-Built Modules

Most of the time, you should be able to build your visualization using pre-built modules. To do this, you don't need to worry about HTML and JavaScript at all, and only look at the documentation for the particular module you want to use.

One included module is **CanvasGrid**, which you can use to visualize objects located on grid cells. This is probably good for a good chunk of agent-based models out there, particularly the simpler ones. 

CanvasGrid iterates over every object in every cell of your model's grid (it assumes that your model has a grid named **grid**) and converts it into a dictionary which defines how it will be drawn. It does this via a **portrayal_method**: a function which the user defines, which takes an object as an input and outputs a dictionary with the following keys:
    "Shape": Can be either "circle" or "rect"
        For Circles:
            "r": The radius, defined as a fraction of cell size. r=1 will fill the entire cell.
        For rectangles:
            "w", "h": The width and height of the rectangle, which are in fractions of cell width and height.
    "Color": The color to draw the shape in; needs to be a valid HTML color, e.g."Red" or "#AA08F8"
    "Filled": either "true" or "false", and determines whether the shape is filled or not.
    "Layer": Layer number of 0 or above; higher-numbered layers are drawn above lower-numbered layers.
    (Shapes also have "x" and "x" coordinates, for the x and y of the grid cell in which it is, but CanvasGrid adds those automatically).

For example, suppose for a Schelling model, we want to draw all agents as circles; red ones for the majority (agent type=0), and blue ones for the minority (agent type=1). The function to do this might look like this:
     
    def schelling_draw(agent):
        if agent is None:
            return
        portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}
        if agent.type == 0:
            portrayal["Color"] = "Red"
        else:
            portrayal["Color"] = "Blue"
        return portrayal

In addition, a CanvasGrid needs to know the width and height of the grid (in number of cells), and the width and height in pixels of the grid to draw in the browser. 

To continue our Schelling example: suppose we have a Schelling model with a grid of 10x10, which we want to draw at 500px X 500px. using the portrayal function we wrote above, we would instantiate our visualization element as follows:

    canvas_element = CanvasGrid(schelling_draw, 10, 10, 500, 500)

Then, to launch a server with this grid as the only visualization element:

    server = ModularServer(SchellingModel, [canvas_element], "Schelling")
    server.launch()

## Sub-Classing Modules

In some cases, you may want or need to tweak the internals of an existing visualization module. The best way to do this is to create a subclass of it.

For example, the TextElement module provides an HTML template to render raw text, but nothing else. To use it, we need to create our own subclass, which implements a **render** method to get visualization-ready data (in this case, just a text string) out of a model object.

Suppose we want a module which can get an arbitrary variable out of a model, and display its name and value. Let's create a new subclass:

    from mesa.visualization.ModularTextVisualization import TextElement

    class AttributeElement(TextElement):
        def __init__(self, attr_name):
            '''
            Create a new text attribute element.
            
            Args:
                attr_name: The name of the attribute to extract from the model.
            '''
            self.attr_name = attr_name

        def render(self, model): 
            val = getattr(model, self.attr_name)
            return attr_name + ": " + str(val)

Now, if we wanted to use our new AttributeElement to add the number of happy agents to our Schelling visualization, it might look something like this:

    happy_element = AttributeElement("happy")
    server = ModularServer(SchellingModel, [canvas_element, happy_element], "Schelling")
    server.launch()

Note that, in this case, we only wanted to change the Python-side render method. We're still using the parent module's HTML and JavaScript template.

## Creating New Modules

But what if we want more than just a different Python renderer; we want to substantially change how a module displays in the browser, or create a completely new module. To do this, we need to open up the HTML template as well:

Let's take a look at the internals of TextElement's template. Here it is, in all its glory:

    <div id="element_{{ index }}">
        <script>
            var render = function(data) {
                txt = data;
                $("#element_{{index}}").html(txt);
            };

            $("#element_{{ index }}").data("render", render);
        </script>
    </div>



