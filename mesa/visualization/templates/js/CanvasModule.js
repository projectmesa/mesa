var CanvasModule = function(canvas_width, canvas_height, grid_width, grid_height) {
	// Create the element
	// ------------------

	// Create the tag:
	var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
	canvas_tag += "style='border:1px dotted'></canvas>";
	// Append it to body:
	var canvas = $(canvas_tag)[0];
	//$("body").append(canvas);
	$("#elements").append(canvas);

	// Create the context and the drawing controller:
	var context = canvas.getContext("2d");
	var canvasDraw = new GridVisualization(canvas_width, canvas_height, grid_width, grid_height, context);

	this.render = function(data) {
		canvasDraw.resetCanvas();
		for (var layer in data)
			canvasDraw.drawLayer(data[layer]);
		canvasDraw.drawGridLines("#eee");
	};

	this.reset = function() {
		canvasDraw.resetCanvas();
	};

};
