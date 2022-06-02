var ContinuousVisualization = function(height, width, context, background_src=null) {
	var height = height;
	var width = width;
	var context = context;
    var background = new Image();
    var background_src = background_src;

	this.draw = function(objects) { // https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Drawing_shapes
		for (var i in objects) {
			var p = objects[i];
			if (p.Shape == "rectangle")
				this.drawRectangle(p.x, p.y, p.w, p.h, p.Color, p.Filled);
			if (p.Shape == "circle"){
				this.drawCircle(p.x, p.y, p.r, p.Color, false);
				this.drawRadius(p.x, p.y, p.r, p.heading, p.Color)
			}
			if (p.Shape == "default"){
			    this.drawDefault(p.x, p.y, p.r, p.heading, p.Color)
			}
			if(p.Shape == "triangle"){
			    this.drawTriangle(p.x, p.y, p.r, p.heading, p.Color)
			}
			if(p.Shape == "star"){
			    this.drawStar(p.x, p.y, p.r, p.heading, p.Color)
			}
			if(p.Shape == "smile"){
			    this.drawSmileFace(p.x, p.y, p.r, p.heading, p.Color)
			}
			if(p.Shape == "pentagon"){
			    this.drawPentagon(p.x, p.y, p.r, p.heading, p.Color)
			}
			if(p.Shape == "arrow"){
			    this.drawArrow(p.x, p.y, p.r, p.heading, p.Color)
			}
			if(p.Shape == "plane"){
			    this.drawPlane(p.x, p.y, p.r, p.heading, p.Color)
			}
			if (p.Shape == "ant"){
			    this.drawAnt(p.x, p.y, p.r, p.heading, p.Color)
			}
		}
	};
	this.drawAnt = function(x,y, radius, heading, color){
        var cx = x * width;
		var cy = y * height;
		var r = radius;
        context.save();
		context.strokeStyle = color;
		context.fillStyle = color;
		context.beginPath();
		context.translate( cx, cy);
		context.scale(1,-1);
        context.rotate(heading*Math.PI/180);
		//put points into here:
		context.arc(0, 0, r/6, Math.PI/2, 5 * Math.PI/2, false);
		context.moveTo((r/-5), 0);
		context.arc(r/-5, 0, r/5, Math.PI/2, 5 * Math.PI/2, false);
		context.moveTo((r/5),0);
		context.arc((r/5),0, r/6, Math.PI/2, 5 * Math.PI/2, false);
		context.moveTo((r/4), (r/10));
		context.lineTo((r/2), (r/4));
		context.moveTo((r/4), (r/-10));
		context.lineTo((r/2), (r/-4));
		//put points above here
		context.fill();
		context.stroke();
		context.restore();
    };
	this.drawPlane = function(x, y, radius, heading, color){
        var cx = x * width;
		var cy = y * height;
		var r = radius;
        context.save();

        context.strokeStyle = color;
		context.fillStyle = color;
		context.beginPath();
		context.translate( cx, cy);
		context.scale(1,-1);
		context.rotate(heading*Math.PI/180);
		//add points bellow here

		context.moveTo(r, 0)
		context.lineTo((r*3/4), (r/8)) //1
		context.lineTo((r*4/6), (r/8)) //2
		context.lineTo((r*2/5), (r/2)) //3
		context.lineTo((r*2/7), (r/2)) //4
		context.lineTo((r*2/7), (r/8)) //5
		context.lineTo((r/6), (r/12)) //6
		context.lineTo((r/12), (r/6)) //7
		context.lineTo((r/8), 0) //8
		context.lineTo((r/12), (-r/6)) //9
		context.lineTo((r/6), (-r/12))
		context.lineTo((r*2/7), (-r/8))
		context.lineTo((r*2/7), (-r/2))
		context.lineTo((r*2/5), (-r/2))
		context.lineTo((r*4/6), (-r/8))
        context.lineTo((r*3/4), (-r/8))

		//add points above here
		context.fill();
        context.stroke();
		context.restore();
    }
    this.drawArrow = function(x, y, radius, heading, color){
        var cx = x * width;
		var cy = y * height;
		var r = radius;
        context.save();
        context.strokeStyle = color;
		context.fillStyle = color;
		context.beginPath();
		context.translate( cx, cy);
		context.scale(1,-1);
		context.rotate(heading*Math.PI/180);
        //place coordinates bellow
        context.moveTo(r, 0)
        context.lineTo((r*2/3), (r/4))
        context.lineTo((r*2/3), (r/11))
        context.lineTo((r/3), (r/11))
        context.lineTo((r/3), (-r/11))
        context.lineTo((r*2/3),(-r/11))
        context.lineTo((r*2/3),(-r/4))
		context.fill();
        context.stroke();
		context.restore();
    }
    //feedback on how pentagon looks
	this.drawPentagon = function(x, y, radius, heading, color){
	    var cx = x * width;
		var cy = y * height;
		var r = radius;
        context.save();
        context.strokeStyle = color;
		context.fillStyle = color;
		context.beginPath();
		context.translate( cx, cy);
		context.scale(1,-1);
		context.rotate(heading*Math.PI/180);

        //place bellow here
        context.moveTo(r, 0)
		context.lineTo((r/2), (-r*13/15))
		context.lineTo((-r*8/11), (-r*8/13))
		context.lineTo((-r*8/11), (r*8/13))
		context.lineTo((r/2),(r*13/15))
        //points above here

		context.fill();
        context.stroke();
		context.restore();
	};
    //feedback on how smileyface looks
	this.drawSmileFace = function(x, y, radius, heading, color){
	    var cx = x * width;
		var cy = y * height;
		var r = radius;
        context.save();
		context.strokeStyle = color;
		context.fillStyle = color;
		context.beginPath();
		context.translate( cx, cy);
		context.scale(1,-1);
        context.rotate(heading*Math.PI/180);
        //put points into here:
        context.arc(0, 0, r/2, Math.PI/2, 5 * Math.PI/2, false); //Outer layer
        context.moveTo(0, (r/3))
        context.arc(0, 0, r/3, Math.PI/2, 3 * Math.PI/2, true); //Smile
        context.moveTo(0, (r/-6)); // x = r/4 && y = (r * -0.416)
        context.arc(r/-6, r/-6, r/8, 0, Math.PI * 2, true) // left eye
        context.moveTo(0, (r/6))
        context.arc(r/-6, r/6, r/8, 0, Math.PI * 2, true) // right eye
        //put points above here
		context.fill();
		//context.stroke();
		context.restore();
	}
    //feedback on how star looks
	this.drawStar = function(x, y, radius, heading, color){
	    var cx = x * width;
		var cy = y * height;
		var r = radius;
        context.save();
		context.strokeStyle = color;
		context.fillStyle = color;
		context.beginPath();
		context.translate( cx, cy);
		context.scale(1,-1);
        context.rotate(heading*Math.PI/180);
		//put points into here:
        context.moveTo((r/2),0)
		context.lineTo((r/5), (r/10))
		context.lineTo((r/5), (r/2)) // extended arm
		context.lineTo((r/-20), (r/6))
		context.lineTo((r/-3), (r/4))
		context.lineTo((r/-6), 0)
		context.lineTo((r/-3), (r/-4))
		context.lineTo((r/-20), (r/-6))
		context.lineTo((r/5), (r/-2)) // extended arm
		//context.lineTo((r/-10), (r/5))
		context.lineTo((r/5), (r/-10))
		context.lineTo((r/2),0)
		//put points above here
		context.fill();
		context.stroke();
		context.restore();
    };
	this.drawTriangle = function(x,y, radius, heading, color){
        var cx = x * width;
		var cy = y * height;
		var r = radius;
        context.save();
		context.strokeStyle = color;
		context.fillStyle = color;
		context.beginPath();
		context.translate( cx, cy);
		context.scale(1,-1);
        context.rotate(heading*Math.PI/180);
		//put points into here:
		context.moveTo((r/2), 0)
		context.lineTo((r/-3), (r/-3))
		context.lineTo((r/-3), (r/3))
		//put points above here
		context.fill();
		context.restore();
    };
    this.drawDefault = function(x,y, radius, heading, color){
        //p1 (r,0)
        //p2 (-r/2, r/4)
        //p3 (0,0)
        //p4 (-r/2, -r/4)
        var cx = x * width;
		var cy = y * height;
		var r = radius;
        context.save();
		context.strokeStyle = color;
		context.fillStyle = color;
		context.beginPath();
		context.translate(cx, cy);
		context.scale(1,-1);
        context.rotate(heading*Math.PI/180);
		//put points into here:
        context.moveTo((r/2) , 0 );
        context.lineTo((r/-3) , (r/4));
        context.lineTo(0 ,0 );
        context.lineTo((r/-3)  , (r/-4));
        //put points above here
		context.fill();
		context.restore();
    };
	this.drawCircle = function(x, y, radius, color, fill) {
		var cx = x * width;
		var cy = y * height;
		var r = radius;
        context.strokeStyle = color;
		context.fillStyle = color;
		context.beginPath();
		context.arc(cx, cy, r, 0, Math.PI * 2, false);
		context.closePath();
        context.stroke();
		if (fill) {
			context.fillStyle = color;
			context.fill();
		}
	};
    this.drawRadius = function(x, y, radius, heading, color) {
        var cx = x * width;
		var cy = y * height;
		var r = radius;
        context.save()
		context.strokeStyle = color;
		context.fillStyle = color;
		context.beginPath();
		context.translate( cx, cy);
        context.scale(1,-1);
		context.rotate(heading*Math.PI/180);
		context.fillRect(0, 0, 0 + r, 2);
		context.strokeStyle = color;
		context.stroke();
		context.restore();
	};

	this.drawRectangle = function(x, y, w, h, color, fill) {
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
		if(background_src != null){
		    this.drawBackground();
		}
	};
	this.drawBackground = function(){
	    context.globalAlpha = .5;
		background.src = background_src;
        context.drawImage(background,0,0, 500, 500);
        context.globalAlpha = 1;
	}
};

var Simple_Continuous_Module = function(canvas_width, canvas_height, background_src) {
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
	var canvasDraw = new ContinuousVisualization(canvas_width, canvas_height, context, background_src);
	this.render = function(data) {
		canvasDraw.resetCanvas();
		canvasDraw.draw(data);
	};
	this.reset = function() {
		canvasDraw.resetCanvas();
	};
};