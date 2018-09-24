var CanvasModule = function(canvas_width, canvas_height, grid_width, grid_height, simulations) {
	// Create the element
	// ------------------
	var simulations = simulations
	var canvasDraw = []
	// Create the tag:
	for (i=0; i<simulations; i++) {
	//$("body").append(canvas);
		var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
		canvas_tag += "style=' id:sim_" + i + " border:1px dotted'></canvas>";
		// Append it to body:
		var canvas = $(canvas_tag)[0];
		var col_width = 12 / simulations
		var col_tag = "<div class='col-xs-" + col_width + "'></div>"
		var col = $(col_tag)[0]
		col.append(canvas)
		elements.append(col)
		// Create the context and the drawing controller:
		var context = canvas.getContext("2d");
		var grid = new GridVisualization(canvas_width, canvas_height, grid_width, grid_height, context)
		canvasDraw.push(grid);
		console.log(canvasDraw)
	}

	

	this.render = function(data, sim) {
		console.log(canvasDraw)
		canvasDraw[sim].resetCanvas();
		for (var layer in data)
			canvasDraw[sim].drawLayer(data[layer]);
		canvasDraw[sim].drawGridLines("#eee");
	};

	this.reset = function() {
		for (i=0; i<simulations; i++) {
			canvasDraw[i].resetCanvas();
		}
	};

};
