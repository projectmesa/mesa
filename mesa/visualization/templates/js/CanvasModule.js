const CanvasModule = function(canvas_width, canvas_height, grid_width, grid_height) {
	// Create the element
	// ------------------

	// Create the tag with absolute positioning :
	const canvas_tag = `<canvas width="${canvas_width}" height="${canvas_height}" class="world-grid"/>`

	const parent_div_tag = '<div style="height:' + canvas_height + 'px;" class="world-grid-parent"></div>'

	// Append it to body:
	const canvas = $(canvas_tag)[0];
	const interaction_canvas = $(canvas_tag)[0];
	const parent = $(parent_div_tag)[0];

	//$("body").append(canvas);
	$("#elements").append(parent);
	parent.append(canvas);
	parent.append(interaction_canvas);

	// Create the context for the agents and interactions and the drawing controller:
	const context = canvas.getContext("2d");

	// Create an interaction handler using the
	const interactionHandler = new InteractionHandler(canvas_width, canvas_height, grid_width, grid_height, interaction_canvas.getContext("2d"));
	const canvasDraw = new GridVisualization(canvas_width, canvas_height, grid_width, grid_height, context, interactionHandler);

	this.render = function(data) {
		canvasDraw.resetCanvas();
		for (const layer in data)
			canvasDraw.drawLayer(data[layer]);
		canvasDraw.drawGridLines("#eee");
	};

	this.reset = function() {
		canvasDraw.resetCanvas();
	};

};
