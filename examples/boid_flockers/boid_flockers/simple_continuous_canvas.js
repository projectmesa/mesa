var ContinuousVisualization = function(height, width, context) {
	var height = height;
	var width = width;
	var context = context;

	this.draw = function(objects) {
		for (var i in objects) {
			var p = objects[i];
			if (p.Shape == "rect")
				this.drawRectange(p.x, p.y, p.w, p.h, p.Color, p.Filled);
			if (p.Shape == "circle")
				this.drawCircle(p.x, p.y, p.r, p.Color, p.Filled);
		};

	};

	this.drawCircle = function(x, y, radius, color, fill) {
		var cx = x * width;
		var cy = y * height;
		var r = radius;

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

	this.drawRectange = function(x, y, w, h, color, fill) {
		context.beginPath();
		var dx = w * width;
		var dy = h * height;

		// Keep the drawing centered:
		var x0 = (x*width) - 0.5*dx;
		var y0 = (y*height) - 0.5*dy;

		context.strokeStyle = color;
		context.fillStyle = color;
		if (fill)
			context.fillRect(x0, y0, dx, dy);
		else
			context.strokeRect(x0, y0, dx, dy);
	};

	this.resetCanvas = function() {
		context.clearRect(0, 0, height, width);
		context.beginPath();
	};
};

var Simple_Continuous_Module = function(canvas_width, canvas_height) {
	// Create the element
	// ------------------

	// Create the tag:
	var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
	canvas_tag += "style='border:1px dotted'></canvas>";
	// Append it to body:
	var canvas = $(canvas_tag)[0];
	$("#elements").append(canvas);

	// Create the context and the drawing controller:
	var context = canvas.getContext("2d");
	var canvasDraw = new ContinuousVisualization(canvas_width, canvas_height, context);

	this.render = function(data) {
		canvasDraw.resetCanvas();
		canvasDraw.draw(data);
	};

	this.reset = function() {
		canvasDraw.resetCanvas();
	};

};