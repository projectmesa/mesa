var PyPlotModule = function(canvas_width, canvas_height) {
    var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
    canvas_tag += "style='border:1px dotted'></canvas>";
    var canvas = $(canvas_tag)[0];
    $("#elements").append(canvas);
    var context = canvas.getContext("2d");


    this.render = function(data) {
        image_data = data[1]
        var image = new Image();
        image.onload = function() {
            var hRatio = canvas.width / image.width    ;
            var vRatio = canvas.height / image.height  ;
            var ratio  = Math.min ( hRatio, vRatio );
            context.drawImage(image, 0,0, image.width, image.height, 0,0,image.width*ratio, image.height*ratio);
        };
        image.src = "data:image/png;base64,"+image_data;

    };

    this.reset = function() {
    };
};
