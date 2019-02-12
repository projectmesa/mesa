/**
Mesa Canvas Grid Visualization
====================================================================

This is JavaScript code to visualize a Mesa Grid or MultiGrid state using the
HTML5 Canvas. Here's how it works:

On the server side, the model developer will have assigned a portrayal to each
agent type. The visualization then loops through the grid, for each object adds
a JSON object to an inner list (keyed on layer) of lists to be sent to the
browser.

Each JSON object to be drawn contains the following fields: Shape (currently
only rectanges and circles are supported), x, y, Color, Filled (boolean),
Layer; circles also get a Radius, while rectangles get x and y sizes. The
latter values are all between [0, 1] and get scaled to the grid cell.

The browser (this code, in fact) then iteratively draws them in, one layer at a
time. Thus, it should be possible to turn different layers on and off.

Here's a sample input, for a 2x2 grid with one layer being cell colors and the
other agent locations, represented by circles:

{"Shape": "rect", "x": 0, "y": 0, "Color": ["#00aa00", "#aa00aa"], "stroke_color": "red", "Filled": "true", "Layer": 0}

{0:[
        {"Shape": "rect", "x": 0, "y": 0, "w": 1, "h": 1,"Color": ["#00aa00", "#aa00aa"], "stroke_color": "red", "Filled": "true", "Layer": 0},
        {"Shape": "rect", "x": 0, "y": 1, "w": 1, "h": 1, "Color": ["#00aa00", "#aa00aa"], "stroke_color": "red", "Filled": "true", "Layer": 0},
        {"Shape": "rect", "x": 1, "y": 0, "w": 1, "h": 1, "Color": ["#00aa00", "#aa00aa"], "stroke_color": "red", "Filled": "true", "Layer": 0},
        {"Shape": "rect", "x": 1, "y": 1, "w": 1, "h": 1, "Color": ["#00aa00", "#aa00aa"], "stroke_color": "red", "Filled": "true", "Layer": 0}
   ],
 1:[
        {"Shape": "circle", "x": 0, "y": 0, "r": 0.5, "Color": ["#00aa00", "#aa00aa"], "stroke_color": "red", "Filled": "true", "Layer": 1, "text": 'A', "text_color": "white"},
        {"Shape": "circle", "x": 1, "y": 1, "r": 0.5, "Color": ["#00aa00", "#aa00aa"], "stroke_color": "red", "Filled": "true", "Layer": 1, "text": 'B', "text_color": "white"}
        {"Shape": "arrowHead", "x": 1, "y": 0, "heading_x": -1, heading_y: 0, "scale": 0.5, "Color": ["#00aa00", "#aa00aa"], "stroke_color": "red", "Filled": "true", "Layer": 1, "text": 'C', "text_color": "white"}
   ]
}

*/

var GridVisualization = function(width, height, gridWidth, gridHeight, num_agents, context, interactionHandler) {
        // Uses Newton's algorithm to check whether num_agents is a perfect square.
        // If it is, returns it's square root
        // If it is not, finds the next perfect square's root
        getNextPerfectSquareRoot = function(num_agents) {
            var x = num_agents;
            var y = Math.floor((x + 1)/ 2);
            while (y < x){
                x = y;
                y = Math.floor((x + Math.floor(num_agents / x)) / 2);
            }
            if (x*x == num_agents){
                return Math.sqrt(num_agents);
            }
            var intRoot = Math.floor(Math.sqrt(num_agents));
            var intRoot = intRoot +1;
            return intRoot;
        }
        // Find macro cell size:
        var cellWidth = Math.floor(width / gridWidth);
        var cellHeight = Math.floor(height / gridHeight);

        // Find micro cell size
        var numPartitions = getNextPerfectSquareRoot(num_agents);
        var microCellWidth = Math.floor(cellWidth / numPartitions);
        var microCellHeight = Math.floor(cellHeight / numPartitions);


        // Find max radius of the circle that can be inscribed (fit) into the
        // cell of the grid.
        var manyMaxR = Math.min(microCellHeight, microCellWidth)/2 - 1;
        var fewMaxR = Math.min(cellHeight, cellWidth)/2 - 1;

        // Calls the appropriate shape(agent)
        this.drawLayer = function(portrayalLayer) {

            // Re-initialize the lookup table
            (interactionHandler) ? interactionHandler.mouseoverLookupTable.init() : null

            for (var i in portrayalLayer) {
                var p = portrayalLayer[i];

                // If p.Color is a string scalar, cast it to an array.
                // This is done to maintain backwards compatibility
                if (!Array.isArray(p.Color))
                    p.Color = [p.Color];

                // Does the inversion of y positioning because of html5
                // canvas y direction is from top to bottom. But we
                // normally keep y-axis in plots from bottom to top.
                p.y = gridHeight - p.y - 1;

                // if a handler exists, add coordinates for the portrayalLayer index
                (interactionHandler) ? interactionHandler.mouseoverLookupTable.set(p.x, p.y, i) : null;

                // If the stroke color is not defined, then the first color in the colors array is the stroke color.
                if (!p.stroke_color)
                    p.stroke_color = p.Color[0];

                // Specifications for drawing objects for multiple option. 
                // Multiple is the number of times the times i goes into numPartitions. Controls the y-axis.
                // Remainder is the remainder of that division. Controls the x axis
                multiple = Math.floor(i/numPartitions)
                remainder = i%numPartitions

                if (p.Shape == "rect"){
                    this.drawRectangle(p.x, p.y, p.w, p.h, p.Color, p.stroke_color, p.Filled, p.text, p.text_color, p.Many, multiple, remainder);
                }
                else if (p.Shape == "circle"){
                    this.drawCircle(p.x, p.y, p.r, p.Color, p.stroke_color, p.Filled, p.text, p.text_color, p.Many, multiple, remainder);
                }
                else if (p.Shape == "arrowHead")
                    this.drawArrowHead(p.x, p.y, p.heading_x, p.heading_y, p.scale, p.Color, p.stroke_color, p.Filled, p.text, p.text_color, p.Many, multiple, remainder);
                else
                    this.drawCustomImage(p.Shape, p.x, p.y, p.scale, p.text, p.text_color, p.Many, multiple, remainder)
            }
            // if a handler exists, update its mouse listeners with the new data
            (interactionHandler) ? interactionHandler.updateMouseListeners(portrayalLayer): null;
        };

        // DRAWING METHODS
        // =====================================================================

        /**
        Draw a circle in the specified grid cell.
        x, y: Grid coords
        r: Radius, as a multiple of cell size
        colors: List of colors for the gradient. Providing only one color will fill the shape with only that color, not gradient.
        stroke_color: Color to stroke the shape
        fill: Boolean for whether or not to fill the circle.
        text: Inscribed text in rectangle.
        text_color: Color of the inscribed text.
        many: Boolean for whether or not to print all of the agents in a state independently
        multiple: the number of times the current agent number i goes into the next perfect square root. Controls y-axis location.
        remainder: the remainder of the division of i/next perfect square root. Controls x-axis location.
        */
        this.drawCircle = function(x, y, radius, colors, stroke_color, fill, text, text_color, many, multiple, remainder) {
            if (many) {
                var r = radius * manyMaxR;
                var cx = x*cellWidth + 2*r + remainder*(microCellWidth);
                var cy = y*cellHeight + 2*r + multiple*(microCellHeight);
            }
            else{
                var r = radius * fewMaxR;
                var cx = (x + 0.5) * cellWidth;
                var cy = (y + 0.5) * cellHeight;
            }
            

            context.beginPath();
            context.arc(cx, cy, r, 0, Math.PI * 2, false);
            context.closePath();

            context.strokeStyle = stroke_color;
            context.stroke();

            if (fill) {
                var gradient = context.createRadialGradient(cx, cy, r, cx, cy, 0);

                for (i = 0; i < colors.length; i++) {
                    gradient.addColorStop(i/colors.length, colors[i]);
                }

                context.fillStyle = gradient;
                context.fill();
            }

            // This part draws the text inside the Circle
            if (text !== undefined) {
                context.fillStyle = text_color;
                context.textAlign = 'center';
                context.textBaseline= 'middle';
                context.fillText(text, cx, cy);
            }

        };

        /**
        Draw a rectangle in the specified grid cell.
        x, y: Grid coords
        w, h: Width and height, [0, 1]
        colors: List of colors for the gradient. Providing only one color will fill the shape with only that color, not gradient.
        stroke_color: Color to stroke the shape
        fill: Boolean, whether to fill or not.
        text: Inscribed text in rectangle.
        text_color: Color of the inscribed text.
        many: Boolean for whether or not to print all of the agents in a state independently
        multiple: the number of times the current agent number i goes into the next perfect square root. Controls y-axis location.
        remainder: the remainder of the division of i/next perfect square root. Controls x-axis location.
        */
        this.drawRectangle = function(x, y, w, h, colors, stroke_color, fill, text, text_color, many, multiple, remainder) {
            context.beginPath();
            // TODO: Support different values of w and h when multiple = True
            if (many){
                var dx = microCellWidth;
                var dy = microCellHeight;
                var x0 = (x*cellWidth)+ 1 + remainder*microCellWidth;
                var y0 = (y*cellHeight)+ 1 + multiple*microCellHeight;
            }
            else{
                var dx = w * cellWidth;
                var dy = h * cellHeight;
                var x0 = (x + 0.5) * cellWidth - dx/2;
                var y0 = (y + 0.5) * cellHeight - dy/2;
            }

            // Keep in the center of the cell:


            context.strokeStyle = stroke_color;
            context.strokeRect(x0, y0, dx, dy);

            if (fill) {
                var gradient = context.createLinearGradient(x0, y0, x0 + microCellWidth, y0 + microCellHeight);

                for (i = 0; i < colors.length; i++) {
                        gradient.addColorStop(i/colors.length, colors[i]);
                }

                // Fill with gradient
                context.fillStyle = gradient;
                context.fillRect(x0,y0,dx,dy);
            }

            // This part draws the text inside the Rectangle
            if (text !== undefined) {
                if (many){
                    var cx = (x*cellWidth) + 1 + remainder*microCellWidth+dx/2;
                    var cy = (y*cellHeight) + 1 + multiple*microCellHeight+dy/2;
                }
                else{
                    var cx = (x + 0.5) * cellWidth;
                    var cy = (y + 0.5) * cellHeight;
                }
                context.fillStyle = text_color;
                context.textAlign = 'center';
                context.textBaseline= 'middle';
                context.fillText(text, cx, cy);
            }
        };

        /**
        Draw an arrow head in the specified grid cell.
        x, y: Grid coords
        s: Scaling of the arrowHead with respect to cell size[0, 1]
        colors: List of colors for the gradient. Providing only one color will fill the shape with only that color, not gradient.
        stroke_color: Color to stroke the shape
        fill: Boolean, whether to fill or not.
        text: Inscribed text in shape.
        text_color: Color of the inscribed text.
        many: Boolean for whether or not to print all of the agents in a state independently
        multiple: the number of times the current agent number i goes into the next perfect square root. Controls y-axis location.
        remainder: the remainder of the division of i/next perfect square root. Controls x-axis location.
        */
        this.drawArrowHead = function(x, y, heading_x, heading_y, scale, colors, stroke_color, fill, text, text_color, many, multiple, remainder) {
            if (many){
                //scale currently doesn't affect the drawings when many is true
                var arrowR = manyMaxR;
                var cx = x*cellWidth + arrowR + remainder*microCellWidth;
                var cy = y*cellHeight + arrowR + multiple*microCellHeight;
            }
            else{
                var arrowR = fewMaxR * scale
                var cx = (x + 0.5) * cellWidth;
                var cy = (y + 0.5) * cellHeight;
            }

            if (heading_x === 0 && heading_y === 1) {
                p1_x = cx;
                p1_y = cy - arrowR;
                p2_x = cx - arrowR;
                p2_y = cy + arrowR;
                p3_x = cx;
                p3_y = cy + 0.8*arrowR;
                p4_x = cx + arrowR;
                p4_y = cy + arrowR;
            }
            else if (heading_x === 1 && heading_y === 0) {
                p1_x = cx + arrowR;
                p1_y = cy;
                p2_x = cx - arrowR;
                p2_y = cy - arrowR;
                p3_x = cx - 0.8*arrowR;
                p3_y = cy;
                p4_x = cx - arrowR;
                p4_y = cy + arrowR;
            }
            else if (heading_x === 0 && heading_y === (-1)) {
                p1_x = cx;
                p1_y = cy + arrowR;
                p2_x = cx - arrowR;
                p2_y = cy - arrowR;
                p3_x = cx;
                p3_y = cy - 0.8*arrowR;
                p4_x = cx + arrowR;
                p4_y = cy - arrowR;
            }
            else if (heading_x === (-1) && heading_y === 0) {
                p1_x = cx - arrowR;
                p1_y = cy;
                p2_x = cx + arrowR;
                p2_y = cy - arrowR;
                p3_x = cx + 0.8*arrowR;
                p3_y = cy;
                p4_x = cx + arrowR;
                p4_y = cy + arrowR;
            }

            context.beginPath();
            context.moveTo(p1_x, p1_y);
            context.lineTo(p2_x, p2_y);
            context.lineTo(p3_x, p3_y);
            context.lineTo(p4_x, p4_y);
            context.closePath();

            context.strokeStyle = stroke_color;
            context.stroke();

            if (fill) {
                var gradient = context.createLinearGradient(p1_x, p1_y, p3_x, p3_y);
                for (i = 0; i < colors.length; i++) {
                    gradient.addColorStop(i/colors.length, colors[i]);
                }
                // Fill with gradient
                context.fillStyle = gradient;
                context.fill();
            }

            // This part draws the text inside the ArrowHead
            if (text !== undefined) {
                if (many){
                    var cx = x*cellWidth + arrowR + remainder*microCellWidth;
                    var cy = y*cellHeight + arrowR + multiple*microCellHeight;
                }
                else{
                    var cx = (x + 0.5) * microCellWidth;
                    var cy = (y + 0.5) * microCellHeight;
                }
                context.fillStyle = text_color
                context.textAlign = 'center';
                context.textBaseline= 'middle';
                context.fillText(text, cx, cy);
            }
    };

    this.drawCustomImage = function (shape, x, y, scale, text, text_color_, many, multiple, remainder) {
        var img = new Image();
            img.src = "local/".concat(shape);
        if (scale === undefined) {
            var scale = 1
        }

        if (many){
            var dWidth = microCellWidth*scale;
            var dHeight = microCellHeight*scale;
            var cx = (x*cellWidth) + scale + remainder*microCellWidth;
            var cy = (y*cellHeight) + scale + multiple*microCellHeight;

            // Coordinates for the text
            var tx = (x*cellWidth) + scale + remainder*microCellWidth + microCellWidth/2;
            var ty = (y*cellHeight) + scale + multiple*microCellHeight + microCellHeight/2;
        }
        else{
            // Calculate coordinates so the image is always centered
            var dWidth = cellWidth * scale;
            var dHeight = cellHeight * scale;
            var cx = x * cellWidth + cellWidth / 2 - dWidth / 2;
            var cy = y * cellHeight + cellHeight / 2 - dHeight / 2;

            // Coordinates for the text
            var tx = (x + 0.5) * cellWidth;
            var ty = (y + 0.5) * cellHeight;
        }




        img.onload = function() {
                context.drawImage(img, cx, cy, dWidth, dHeight);
                // This part draws the text on the image
                if (text !== undefined) {
                    // ToDo: Fix fillStyle
                    // context.fillStyle = text_color;
                    context.textAlign = 'center';
                    context.textBaseline= 'middle';
                    context.fillText(text, tx, ty);
                }
        }
        }

        /**
        Draw Grid lines in the full grid
        */

        this.drawGridLines = function() {
            context.beginPath();
            context.strokeStyle = "#eee";
            maxX = cellWidth * gridWidth;
            maxY = cellHeight * gridHeight;


            // Draw horizontal grid lines:
            for(var y=0; y<=maxY; y+=cellHeight) {
                context.moveTo(0, y+0.5);
                context.lineTo(maxX, y+0.5);
            }
            // Draw vertical grid lines:
            for(var x=0; x<=maxX; x+= cellWidth) {
                context.moveTo(x+0.5, 0);
                context.lineTo(x+0.5, maxY);
            }

            context.stroke();
        };

        this.resetCanvas = function() {
            context.clearRect(0, 0, width, height);
            context.beginPath();
        };

};
