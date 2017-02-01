/**
Mesa Canvas Grid Visualization
====================================================================

This is JavaScript code to visualize a Mesa Grid or MultiGrid state using the
HTML5 Canvas. Here's how it works:

On the server side, the model developer will have assigned a portrayal to each
agent type. The visualization then loops through the grid, for each object adds
a JSON object to an inner list (keyed on layer) of lists to be sent to the
browser.

Each JSON object to be drawn contains the following fields: Shape (currently
only rectanges and circles are supported), x, y, Color, Filled (boolean),
Layer; circles also get a Radius, while rectangles get x and y sizes. The
latter values are all between [0, 1] and get scaled to the grid cell.

The browser (this code, in fact) then iteratively draws them in, one layer at a
time. Thus, it should be possible to turn different layers on and off.

Here's a sample input, for a 2x2 grid with one layer being cell colors and the
other agent locations, represented by circles:

{"Shape": "rect", "x": 0, "y": 0, "Color": "#00aa00", "Filled": "true", "Layer": 0}

{0:[
        {"Shape": "rect", "x": 0, "y": 0, "w": 1, "h": 1, "Color": "#00aa00", "Filled": "true", "Layer": 0},
	{"Shape": "rect", "x": 0, "y": 1, "w": 1, "h": 1, "Color": "#00aa00", "Filled": "true", "Layer": 0},
	{"Shape": "rect", "x": 1, "y": 0, "w": 1, "h": 1, "Color": "#00aa00", "Filled": "true", "Layer": 0},
	{"Shape": "rect", "x": 1, "y": 1, "w": 1, "h": 1, "Color": "#00aa00", "Filled": "true", "Layer": 0}
   ],
 1:[
	{"Shape": "circle", "x": 0, "y": 0, "r": 0.5, "Color": "#AAAAAA", "Filled": "true", "Layer": 1, "text": 'A', "text_color": "white"},
	{"Shape": "circle", "x": 1, "y": 1, "r": 0.5, "Color": "#AAAAAA", "Filled": "true", "Layer": 1, "text": 'B', "text_color": "white"}
	{"Shape": "arrowHead", "x": 1, "y": 0, "heading_x": -1, heading_y: 0, "scale": 0.5, "Color": "green", "Filled": "true", "Layer": 1, "text": 'C', "text_color": "white"}
   ]
}

*/

var GridVisualization = function(width, height, gridWidth, gridHeight, context) {
	var width = width;
	var height = height;
	var gridWidth = gridWidth;
	var gridHeight = gridHeight;
	var context = context;

	// Find cell size:
	var cellWidth = Math.floor(width / gridWidth);
	var cellHeight = Math.floor(height / gridHeight);

        // Find max radius of the circle that can be inscribed (fit) into the
        // cell of the grid.
	var maxR = Math.min(cellHeight, cellWidth)/2 - 1;

	// Calls the appropriate shape(agent)
        this.drawLayer = function(portrayalLayer) {
		for (var i in portrayalLayer) {
			var p = portrayalLayer[i];
                        // Does the inversion of y positioning because of html5
                        // canvas y direction is from top to bottom. But we
                        // normally keep y-axis in plots from bottom to top.
                        p.y = gridHeight - p.y - 1;
			if (p.Shape == "rect")
				this.drawRectangle(p.x, p.y, p.w, p.h, p.Color, p.Filled, p.text, p.text_color);
			else if (p.Shape == "circle")
				this.drawCircle(p.x, p.y, p.r, p.Color, p.Filled, p.text, p.text_color);
                        else if (p.Shape == "arrowHead")
				this.drawArrowHead(p.x, p.y, p.heading_x, p.heading_y, p.scale, p.Color, p.Filled, p.text, p.text_color);
		}
	};

	// DRAWING METHODS
	// =====================================================================

	/**
	Draw a circle in the specified grid cell.
	x, y: Grid coords
	r: Radius, as a multiple of cell size
	color: Code for the fill color
	fill: Boolean for whether or not to fill the circle.
        text: Inscribed text in rectangle.
        text_color: Color of the inscribed text.
        */
	this.drawCircle = function(x, y, radius, color, fill, text, text_color) {
		var cx = (x + 0.5) * cellWidth;
		var cy = (y + 0.5) * cellHeight;
		var r = radius * maxR;

		context.beginPath();
		context.arc(cx, cy, r, 0, Math.PI * 2, false);
		context.closePath();

		context.strokeStyle = color;
		context.stroke();

		if (fill) {
			context.fillStyle = color;
			context.fill();
		}

                // This part draws the text inside the Circle
                if (text !== undefined) {
                        context.fillStyle = text_color;
                        context.textAlign = 'center';
                        context.textBaseline= 'middle';
                        context.fillText(text, cx, cy);
                }

	};

	/**
	Draw a rectangle in the specified grid cell.
	x, y: Grid coords
	w, h: Width and height, [0, 1]
	color: Color for the rectangle
	fill: Boolean, whether to fill or not.
        text: Inscribed text in rectangle.
        text_color: Color of the inscribed text.
	*/
	this.drawRectangle = function(x, y, w, h, color, fill, text, text_color) {
		context.beginPath();
		var dx = w * cellWidth;
		var dy = h * cellHeight;

		// Keep in the center of the cell:
		var x0 = (x + 0.5) * cellWidth - dx/2;
		var y0 = (y + 0.5) * cellHeight - dy/2;

		context.strokeStyle = color;
		context.fillStyle = color;
		if (fill)
			context.fillRect(x0, y0, dx, dy);
		else
			context.strokeRect(x0, y0, dx, dy);

                // This part draws the text inside the Rectangle
                if (text !== undefined) {
                        var cx = (x + 0.5) * cellWidth;
                        var cy = (y + 0.5) * cellHeight;
                        context.fillStyle = text_color;
                        context.textAlign = 'center';
                        context.textBaseline= 'middle';
                        context.fillText(text, cx, cy);
                }
	};

        /**
	Draw an arrow head in the specified grid cell.
	x, y: Grid coords
	s: Scaling of the arrowHead with respect to cell size[0, 1]
	color: Color for the shape
	fill: Boolean, whether to fill or not.
        text: Inscribed text in shape.
        text_color: Color of the inscribed text.
	*/
        this.drawArrowHead = function(x, y, heading_x, heading_y, scale, color, fill, text, text_color) {
                arrowR = maxR * scale;
		var cx = (x + 0.5) * cellWidth;
		var cy = (y + 0.5) * cellHeight;
                if (heading_x === 0 && heading_y === 1) {
                        p1_x = cx;
                        p1_y = cy - arrowR;
                        p2_x = cx - arrowR;
                        p2_y = cy + arrowR;
                        p3_x = cx;
                        p3_y = cy + 0.8*arrowR;
                        p4_x = cx + arrowR;
                        p4_y = cy + arrowR;
                }
                else if (heading_x === 1 && heading_y === 0) {
                        p1_x = cx + arrowR;
                        p1_y = cy;
                        p2_x = cx - arrowR;
                        p2_y = cy - arrowR;
                        p3_x = cx - 0.8*arrowR;
                        p3_y = cy;
                        p4_x = cx - arrowR;
                        p4_y = cy + arrowR;
                }
                else if (heading_x === 0 && heading_y === (-1)) {
                        p1_x = cx;
                        p1_y = cy + arrowR;
                        p2_x = cx - arrowR;
                        p2_y = cy - arrowR;
                        p3_x = cx;
                        p3_y = cy - 0.8*arrowR;
                        p4_x = cx + arrowR;
                        p4_y = cy - arrowR;
                }
                else if (heading_x === (-1) && heading_y === 0) {
                        p1_x = cx - arrowR;
                        p1_y = cy;
                        p2_x = cx + arrowR;
                        p2_y = cy - arrowR;
                        p3_x = cx + 0.8*arrowR;
                        p3_y = cy;
                        p4_x = cx + arrowR;
                        p4_y = cy + arrowR;
                }

		context.beginPath();
                context.moveTo(p1_x, p1_y);
                context.lineTo(p2_x, p2_y);
                context.lineTo(p3_x, p3_y);
                context.lineTo(p4_x, p4_y);
		context.closePath();

		context.strokeStyle = color;
		context.stroke();

		if (fill) {
			context.fillStyle = color;
			context.fill();
		}

                // This part draws the text inside the ArrowHead
                if (text !== undefined) {
        		var cx = (x + 0.5) * cellWidth;
                  	var cy = (y + 0.5) * cellHeight;
                        context.fillStyle = text_color
                        context.textAlign = 'center';
                        context.textBaseline= 'middle';
                        context.fillText(text, cx, cy);
                }
        };

	/**
        Draw Grid lines in the full gird
        */

	this.drawGridLines = function() {
		context.beginPath();
		context.strokeStyle = "#eee";
		maxX = cellWidth * gridWidth;
		maxY = cellHeight * gridHeight;

		// Draw horizontal grid lines:
		for(var y=0; y<=maxY; y+=cellHeight) {
			context.moveTo(0, y+0.5);
			context.lineTo(maxX, y+0.5);
		}

		for(var x=0; x<=maxX; x+= cellWidth) {
			context.moveTo(x+0.5, 0);
			context.lineTo(x+0.5, maxY);
		}

		context.stroke();
	};

	this.resetCanvas = function() {
		context.clearRect(0, 0, width, height);
		context.beginPath();
	};

};
