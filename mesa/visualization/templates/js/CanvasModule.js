var CanvasModule = function(canvas_width, canvas_height, grid_width, grid_height, simulations) {

	var simulations = simulations
	var canvasDraw = []
	var col_width = 12 / simulations

	for (let i=0; i<simulations; i++) {

		let col = document.createElement("div");
		col.classList.add("col-xs-" + col_width);

		canvas = document.createElement("canvas")
		canvas.width = canvas_width;
		canvas.height = canvas_height;
		canvas.id = "sim_" + i;

		let context = canvas.getContext("2d");
		let grid = new GridVisualization(canvas_width, canvas_height, grid_width, grid_height, context);

		canvasDraw.push(grid);

		col.append(canvas);
		document.getElementById("elements").append(col);
	}
	
	this.render = function(data, sim) {
		// render data of simulation sim
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
