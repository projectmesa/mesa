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

## Module Internals

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

This isn't a full HTML page, obviously -- it's a chunk of HTML code to be inserted into the proper place in the larger visualization page template. Anywhere you see {{curly_braces}} is a template -- the server will replace it with the value of the variable inside it when the page is created. If the element is being created with an argument of index=0, the div id will be element_0, for example.

At the moment, the outer tag needs to stay constant. Each element is instantiated with an index, which is its order on the page. This provides a unique identifier which tells the page where to send each piece of visualization data it receives from the server. The first visualization element on the page will have id="element_0", the second one "element_1", etc.

In this case, there is no other HTML code in the div. This is because it is going to hold unformatted text, and nothing else. 

The next section is important: the script tag stores the code that's used to render the data. First, it creates a function called 'render': all this function does is use JQuery to replace the HTML contents of its own div with the text it gets as an input. Once the function is defined, the next command uses JQuery to associate the function with the key "render", all of which in turn is associated with the element. In Python terms, you can think of the webpage having a dictionary, which will look something like

    {
        "#element_0": 
            {"render": render},
        ...
    }

To help understand why it looks like this, here's a snippet of JavaScript from the overall visualization template itself, on how to handle incoming data:

    elements = msg["data"]
    for (var i in elements) {
        var element = elements[i];
        var render = $("#element_" + i).data("render");
        render(element);
    }

Data to visualize arrive over the websocket as a list. For each index of the list, the code gest the "render" function associated with the appropriate "element_" div, and then passes the list item associated with that index.

Currently, module HTML templates live in the *mesa/visualization/templates* directory, as html files. Each module's Python class has a *template* attribute, with the name of the HTML template (for example, "text_module.html"). 

When creating a new module, the Python and JavaScript code need to be written in synch: the module Python-side **render** method needs to output data in the exact same format that the JavaScript **render** function receives as an input.



