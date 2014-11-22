/*
Mesa Canvas Grid Visualization
====================================================================

This is JavaScript code to visualize a Mesa Grid or MultiGrid state using the 
HTML5 Canvas. Here's how it works:

On the server side, the model developer will have assigned a portrayal to each
agent type. The visualization then loops through the grid, for each object adds
a JSON object to an inner list (keyed on layer) of lists to be sent to the browser. 

Each JSON object to be drawn contains the following fields: Shape (currently 
only rectanges and circles are supported), x, y, Color, Filled (boolean), Layer; 
circles also get a Radius, while rectangles get x and y sizes. The latter values
are all between [0, 1] and get scaled to the grid cell.

The browser (this code, in fact) then iteratively draws them in, one layer at a time. Thus, it 
should be possible to turn different layers on and off. 

Here's a sample input, for a 2x2 grid with one layer being cell colors and the other agent 
locations, represented by circles:

{"Shape": "rect", "x": 0, "y": 0, "Color": "#00aa00", "Filled": "true", "Layer": 0}

{0:[{"Shape": "rect", "x": 0, "y": 0, "w": 1, "h": 1, "Color": "#00aa00", "Filled": "true", "Layer": 0},
	{"Shape": "rect", "x": 0, "y": 0, "w": 1, "h": 1, "Color": "#00aa00", "Filled": "true", "Layer": 0},
	{"Shape": "rect", "x": 0, "y": 0, "w": 1, "h": 1, "Color": "#00aa00", "Filled": "true", "Layer": 0},
	{"Shape": "rect", "x": 0, "y": 0, "w": 1, "h": 1, "Color": "#00aa00", "Filled": "true", "Layer": 0} 
   ],
 1: [
	{"Shape": "circle", "x": 0, "y": 0, "r": 0.5, "Color": "#AAAAAA", "Filled": "true", "Layer": 1},
	{"Shape": "circle", "x": 1, "y": 1, "r": 0.5, "Color": "#AAAAAA", "Filled": "true", "Layer": 1}
   ]
}

*/

var GridVisualization = function(height, width, gridHeight, gridWidth, context) {
	var height = height;
	var width = width;
	var gridHeight = gridHeight;
	var gridWidth = gridWidth;
	var context = context;

	// Find cell size:
	var cellHeight = Math.floor(height / gridHeight);
	var cellWidth = Math.floor(width / gridWidth);

	var maxR = Math.min(cellHeight, cellWidth)/2 - 1;


	this.drawLayer = function(portrayalLayer) {
		for (var i in portrayalLayer) {
			var p = portrayalLayer[i];
			if (p.Shape == "rect")
				this.drawRectange(p.x, p.y, p.w, p.h, p.Color, p.Filled);
			if (p.Shape == "circle")
				this.drawCircle(p.x, p.y, p.r, p.Color, p.Filled);
		}
	};



	//   DRAWING METHODS
	//  =====================================================================
	
	/**
		Draw a circle in the specified grid cell.
		x, y: Grid coords
		r: Radius, as a multiple of cell size
		color: Code for the fill color
		fill: Boolean for whether or not to fill the circle.
	*/
	this.drawCircle = function(x, y, radius, color, fill) {
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

	};

	/**
		Draw a rectangle in the specified grid cell.
		x, y: Grid coords
		w, h: Width and height, [0, 1]
		color: Color for the rectangle
		fill: Boolean, whether to fill or not.
	*/
	this.drawRectange = function(x, y, w, h, color, fill) {
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
	};

	/**
		Draw a rectangle in the specified grid cell.
		x, y: Grid coords
		w, h: Width and height, [0, 1]
		color: Color for the rectangle
		fill: Boolean, whether to fill or not.
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
		context.clearRect(0, 0, height, width);
		context.beginPath();
	};

};