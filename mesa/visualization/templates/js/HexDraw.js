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

var HexVisualization = function(width, height, gridWidth, gridHeight, context, interactionHandler) {

	// Find cell size:
	var cellWidth = Math.floor(width / gridWidth);
	var cellHeight = Math.floor(height / gridHeight);

        // Find max radius of the circle that can be inscribed (fit) into the
        // cell of the grid.
	var maxR = Math.min(cellHeight, cellWidth)/2 - 1;

	// Configure the interaction handler to use a hex coordinate mapper
  (interactionHandler) ? interactionHandler.setCoordinateMapper("hex") : null;

	// Calls the appropriate shape(agent)
        this.drawLayer = function(portrayalLayer) {
	        // Re-initialize the lookup table
	        (interactionHandler) ? interactionHandler.mouseoverLookupTable.init() : null
		for (var i in portrayalLayer) {
			var p = portrayalLayer[i];
                        // Does the inversion of y positioning because of html5
                        // canvas y direction is from top to bottom. But we
                        // normally keep y-axis in plots from bottom to top.
                        p.y = gridHeight - p.y - 1;

                        // if a handler exists, add coordinates for the portrayalLayer index
                        (interactionHandler) ? interactionHandler.mouseoverLookupTable.set(p.x, p.y, i) : null;

			if (p.Shape == "hex")
				this.drawHex(p.x, p.y, p.r, p.Color, p.Filled, p.text, p.text_color);
			else if (p.Shape == "circle")
				this.drawCircle(p.x, p.y, p.r, p.Color, p.Filled, p.text, p.text_color);
            else if (p.Shape == "arrowHead")
				this.drawArrowHead(p.x, p.y, p.heading_x, p.heading_y, p.scale, p.Color, p.Filled, p.text, p.text_color);
			else
				this.drawCustomImage(p.Shape, p.x, p.y, p.scale, p.text, p.text_color)
		}
		// if a handler exists, update its mouse listeners with the new data
		(interactionHandler) ? interactionHandler.updateMouseListeners(portrayalLayer): null;
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
		if(x % 2 == 0){
			var cy = (y + 0.5) * cellHeight;
		} else {
			var cy = ((y + 0.5) * cellHeight) + cellHeight/2;
		}
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
	Draw a hexagon in the specified grid cell.
	x, y: Grid coords
	r: Radius, as a multiple of cell size
	color: Code for the fill color
	fill: Boolean for whether or not to fill the circle.
        text: Inscribed text in rectangle.
        text_color: Color of the inscribed text.
        */
	this.drawHex = function(x, y, radius, color, fill, text, text_color) {
		var cx = (x + 0.5) * cellWidth;
		if(x % 2 == 0){
			var cy = (y + 0.5) * cellHeight;
		} else {
			var cy = ((y + 0.5) * cellHeight) + cellHeight/2;
		}
		maxHexRadius = cellHeight/Math.sqrt(3)
		var r = radius * maxHexRadius;

		function hex_corner(x,y, size, i){
		    var angle_deg = 60 * i
		    var angle_rad = Math.PI / 180 * angle_deg
		    return [(x + size * Math.cos(angle_rad) * 1.2),
		            (y + size * Math.sin(angle_rad))]
		}


		var px, py
		context.beginPath();
		[px, py] = hex_corner(cx,cy,r,1)
		// console.log(px,py)
		context.moveTo(px,py)
		//for i in range(5):
		Array.from(new Array(5), (n,i) => {
			[px, py] = hex_corner(cx,cy,r,i + 2)
			// console.log(px,py)
			context.lineTo(px,py)
		})
		context.closePath()

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


	this.drawCustomImage = function (shape, x, y, scale, text, text_color_) {
		var img = new Image();
			img.src = "local/".concat(shape);
		if (scale === undefined) {
			var scale = 1
		}
		// Calculate coordinates so the image is always centered
		var dWidth = cellWidth * scale;
		var dHeight = cellHeight * scale;
		var cx = x * cellWidth + cellWidth / 2 - dWidth / 2;
		var cy = y * cellHeight + cellHeight / 2 - dHeight / 2;

		// Coordinates for the text
		var tx = (x + 0.5) * cellWidth;
		var ty = (y + 0.5) * cellHeight;


		img.onload = function() {
			context.drawImage(img, cx, cy, dWidth, dHeight);
			// This part draws the text on the image
			if (text !== undefined) {
				// ToDo: Fix fillStyle
				// context.fillStyle = text_color;
				context.textAlign = 'center';
				context.textBaseline= 'middle';
				context.fillText(text, tx, ty);
			}
		}
	}

	/**
        Draw Grid lines in the full gird
        */

	this.drawGridLines = function(strokeColor) {
		context.beginPath();
		context.strokeStyle = strokeColor || "#eee";
		const maxX = cellWidth * gridWidth;
		const maxY = cellHeight * gridHeight;

		const xStep = cellWidth * 0.33;
		const yStep = cellHeight * 0.5;

		var yStart = yStep;
		for(var x=cellWidth/2; x<=maxX; x+= cellWidth) {
				for(var y=yStart; y<=maxY; y+=cellHeight) {

					context.moveTo(x - 2 * xStep, y);

					context.lineTo(x - xStep, y - yStep)
					context.lineTo(x + xStep, y - yStep)
					context.lineTo(x + 2 * xStep, y )

					context.lineTo(x + xStep, y + yStep )
					context.lineTo(x - xStep, y + yStep )
					context.lineTo(x - 2 * xStep, y)

				}
			yStart = (yStart === 0) ? yStep: 0;
		}

		context.stroke();
	};

	this.resetCanvas = function() {
		context.clearRect(0, 0, width, height);
		context.beginPath();
	};

};
