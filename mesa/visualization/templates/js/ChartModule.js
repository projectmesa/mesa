var ChartModule = function(series, canvas_width, canvas_height) {
	// Create the elements
	
	// Create the tag:
	var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
	canvas_tag += "style='border:1px dotted'></canvas>";
	// Append it to body:
	var canvas = $(canvas_tag)[0];
	//$("body").append(canvas);
	$("#elements").append(canvas);
	// Create the context and the drawing controller:
	var context = canvas.getContext("2d");

	// Prep the chart properties and series:
	var datasets = []
	for (var i in series) {
		var s = series[i];
		var new_series = {label: s.Label, strokeColor: s.Color, data: []};
		datasets.push(new_series);
	}

	var data = {
		labels: [],
		datasets: datasets
	};

	var options = {
		animation: false,
		datasetFill: false,
		pointDot: false,
		bezierCurve : false
	};

	var chart = new Chart(context).Line(data, options);

	this.render = function(data) {
		chart.addData(data, control.tick);
	};

	this.reset = function() {
		chart.destroy();
		data.labels = [];
		chart = new Chart(context).Line(data, options);
	};
};