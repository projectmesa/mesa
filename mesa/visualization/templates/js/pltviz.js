let PyPlotModule = function(canvas_width, canvas_height) {
    let canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
    canvas_tag += "style='border:1px dotted'></canvas>";
    const canvas = $(canvas_tag)[0];
    $("#elements").append(canvas);
    const context = canvas.getContext("2d");

    this.render = function(data) {
        const image_data = data[1]
        const image = new Image();
        image.onload = function() {
            const hRatio = canvas.width / image.width    ;
            const vRatio = canvas.height / image.height  ;
            const ratio  = Math.min ( hRatio, vRatio );
            context.drawImage(image, 0,0, image.width, image.height, 0,0,image.width*ratio, image.height*ratio);
        };
        image.src = "data:image/png;base64,"+image_data;

    };

    this.reset = function() {
    };
};
