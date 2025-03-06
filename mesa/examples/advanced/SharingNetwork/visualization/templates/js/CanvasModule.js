var CanvasModule = function(canvas_width, canvas_height, grid_width, grid_height) {
	// Create the element
	// ------------------

	// Create the tag with absolute positioning :
	var canvas_tag = `<canvas width="${canvas_width}" height="${canvas_height}" class="world-grid"/>`

	var parent_div_tag = '<div style="height:' + canvas_height + 'px;" class="world-grid-parent"></div>'

	// Append it to body:
	var canvas = $(canvas_tag)[0];
	var interaction_canvas = $(canvas_tag)[0];
	var parent = $(parent_div_tag)[0];

	//$("body").append(canvas);
	$("#elements").append(parent);
	parent.append(canvas);
	parent.append(interaction_canvas);

	// Create the context for the agents and interactions and the drawing controller:
	var context = canvas.getContext("2d");

	// Create an interaction handler using the
	var interactionHandler = new InteractionHandler(canvas_width, canvas_height, grid_width, grid_height, interaction_canvas.getContext("2d"));
	var canvasDraw = new GridVisualization(canvas_width, canvas_height, grid_width, grid_height, context, interactionHandler);

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
