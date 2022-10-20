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

const GridVisualization = function (
  width,
  height,
  gridWidth,
  gridHeight,
  context,
  interactionHandler
) {
  // Find cell size:
  const cellWidth = Math.floor(width / gridWidth);
  const cellHeight = Math.floor(height / gridHeight);

  // Find max radius of the circle that can be inscribed (fit) into the
  // cell of the grid.
  const maxR = Math.min(cellHeight, cellWidth) / 2 - 1;

  // Calls the appropriate shape(agent)
  this.drawLayer = function (portrayalLayer) {
    // Re-initialize the lookup table
    interactionHandler ? interactionHandler.mouseoverLookupTable.init() : null;

    for (const i in portrayalLayer) {
      const p = portrayalLayer[i];

      // If p.Color is a string scalar, cast it to an array.
      // This is done to maintain backwards compatibility
      if (!Array.isArray(p.Color)) p.Color = [p.Color];

      // Does the inversion of y positioning because of html5
      // canvas y direction is from top to bottom. But we
      // normally keep y-axis in plots from bottom to top.
      p.y = gridHeight - p.y - 1;

      // if a handler exists, add coordinates for the portrayalLayer index
      interactionHandler
        ? interactionHandler.mouseoverLookupTable.set(p.x, p.y, i)
        : null;

      // If the stroke color is not defined, then the first color in the colors array is the stroke color.
      if (!p.stroke_color) p.stroke_color = p.Color[0];

      // Default alignments to 0.5 (center of a cell)
      p.xAlign ??= 0.5;
      p.yAlign ??= 0.5;

      if (p.Shape == "rect")
        this.drawRectangle(
          p.x,
          p.y,
          p.xAlign,
          p.yAlign,
          p.w,
          p.h,
          p.Color,
          p.stroke_color,
          p.Filled,
          p.text,
          p.text_color
        );
      else if (p.Shape == "circle")
        this.drawCircle(
          p.x,
          p.y,
          p.xAlign,
          p.yAlign,
          p.r,
          p.Color,
          p.stroke_color,
          p.Filled,
          p.text,
          p.text_color
        );
      else if (p.Shape == "arrowHead")
        this.drawArrowHead(
          p.x,
          p.y,
          p.heading_x,
          p.heading_y,
          p.scale,
          p.Color,
          p.stroke_color,
          p.Filled,
          p.text,
          p.text_color
        );
      else
        this.drawCustomImage(p.Shape, p.x, p.y, p.scale, p.text, p.text_color);
    }
    // if a handler exists, update its mouse listeners with the new data
    interactionHandler
      ? interactionHandler.updateMouseListeners(portrayalLayer)
      : null;
  };

  // DRAWING METHODS
  // =====================================================================

  /**
        Draw a circle in the specified grid cell.
        x, y: Grid coords
        xAlign, yAlign: Alignment within the cell, defaults to 0.5 (center)
        r: Radius, as a multiple of cell size
        colors: List of colors for the gradient. Providing only one color will fill the shape with only that color, not gradient.
        stroke_color: Color to stroke the shape
        fill: Boolean for whether or not to fill the circle.
        text: Inscribed text in rectangle.
        text_color: Color of the inscribed text.
        */
  this.drawCircle = function (
    x,
    y,
    xAlign,
    yAlign,
    radius,
    colors,
    stroke_color,
    fill,
    text,
    text_color
  ) {
    // Prevent circle from being drawn outside cell bounds.
    // Since a radius of 1 corresponds to a circle that fills
    // the entire cell, it is necessary to divide radius by 2.
    xAlign = clamp(xAlign, radius / 2, 1 - radius / 2);
    yAlign = clamp(yAlign, radius / 2, 1 - radius / 2);

    const cx = (x + xAlign) * cellWidth;
    const cy = (y + yAlign) * cellHeight;
    const r = radius * maxR;

    context.beginPath();
    context.arc(cx, cy, r, 0, Math.PI * 2, false);
    context.closePath();

    context.strokeStyle = stroke_color;
    context.stroke();

    if (fill) {
      const gradient = context.createRadialGradient(cx, cy, r, cx, cy, 0);

      for (let i = 0; i < colors.length; i++) {
        gradient.addColorStop(i / colors.length, colors[i]);
      }

      context.fillStyle = gradient;
      context.fill();
    }

    // This part draws the text inside the Circle
    if (text !== undefined) {
      context.fillStyle = text_color;
      context.textAlign = "center";
      context.textBaseline = "middle";
      context.fillText(text, cx, cy);
    }
  };

  /**
        Draw a rectangle in the specified grid cell.
        x, y: Grid coords
        xAlign, yAlign: Alignment within the cell, defaults to 0.5 (center)
        w, h: Width and height, [0, 1]
        colors: List of colors for the gradient. Providing only one color will fill the shape with only that color, not gradient.
        stroke_color: Color to stroke the shape
        fill: Boolean, whether to fill or not.
        text: Inscribed text in rectangle.
        text_color: Color of the inscribed text.
        */
  this.drawRectangle = function (
    x,
    y,
    xAlign,
    yAlign,
    w,
    h,
    colors,
    stroke_color,
    fill,
    text,
    text_color
  ) {
    context.beginPath();
    const dx = w * cellWidth;
    const dy = h * cellHeight;

    // Prevent rect from being drawn outside cell bounds.
    xAlign = clamp(xAlign, w / 2, 1 - w / 2);
    yAlign = clamp(yAlign, h / 2, 1 - h / 2);

    const x0 = (x + xAlign) * cellWidth - dx / 2;
    const y0 = (y + yAlign) * cellHeight - dy / 2;

    context.strokeStyle = stroke_color;
    context.strokeRect(x0, y0, dx, dy);

    if (fill) {
      const gradient = context.createLinearGradient(
        x0,
        y0,
        x0 + cellWidth,
        y0 + cellHeight
      );

      for (let i = 0; i < colors.length; i++) {
        gradient.addColorStop(i / colors.length, colors[i]);
      }

      // Fill with gradient
      context.fillStyle = gradient;
      context.fillRect(x0, y0, dx, dy);
    } else {
      context.fillStyle = color;
      context.strokeRect(x0, y0, dx, dy);
    }
    // This part draws the text inside the Rectangle
    if (text !== undefined) {
      const cx = (x + 0.5) * cellWidth;
      const cy = (y + 0.5) * cellHeight;
      context.fillStyle = text_color;
      context.textAlign = "center";
      context.textBaseline = "middle";
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
        */
  this.drawArrowHead = function (
    x,
    y,
    heading_x,
    heading_y,
    scale,
    colors,
    stroke_color,
    fill,
    text,
    text_color
  ) {
    const arrowR = maxR * scale;
    const cx = (x + 0.5) * cellWidth;
    const cy = (y + 0.5) * cellHeight;
    if (heading_x === 0 && heading_y === 1) {
      p1_x = cx;
      p1_y = cy - arrowR;
      p2_x = cx - arrowR;
      p2_y = cy + arrowR;
      p3_x = cx;
      p3_y = cy + 0.8 * arrowR;
      p4_x = cx + arrowR;
      p4_y = cy + arrowR;
    } else if (heading_x === 1 && heading_y === 0) {
      p1_x = cx + arrowR;
      p1_y = cy;
      p2_x = cx - arrowR;
      p2_y = cy - arrowR;
      p3_x = cx - 0.8 * arrowR;
      p3_y = cy;
      p4_x = cx - arrowR;
      p4_y = cy + arrowR;
    } else if (heading_x === 0 && heading_y === -1) {
      p1_x = cx;
      p1_y = cy + arrowR;
      p2_x = cx - arrowR;
      p2_y = cy - arrowR;
      p3_x = cx;
      p3_y = cy - 0.8 * arrowR;
      p4_x = cx + arrowR;
      p4_y = cy - arrowR;
    } else if (heading_x === -1 && heading_y === 0) {
      p1_x = cx - arrowR;
      p1_y = cy;
      p2_x = cx + arrowR;
      p2_y = cy - arrowR;
      p3_x = cx + 0.8 * arrowR;
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
      const gradient = context.createLinearGradient(p1_x, p1_y, p3_x, p3_y);

      for (let i = 0; i < colors.length; i++) {
        gradient.addColorStop(i / colors.length, colors[i]);
      }

      // Fill with gradient
      context.fillStyle = gradient;
      context.fill();
    }

    // This part draws the text inside the ArrowHead
    if (text !== undefined) {
      context.fillStyle = text_color;
      context.textAlign = "center";
      context.textBaseline = "middle";
      context.fillText(text, cx, cy);
    }
  };

  this.drawCustomImage = function (shape, x, y, scale, text, text_color_) {
    const img = new Image();
    img.src = "local/custom/".concat(shape);
    if (scale === undefined) {
      scale = 1;
    }
    // Calculate coordinates so the image is always centered
    const dWidth = cellWidth * scale;
    const dHeight = cellHeight * scale;
    const cx = x * cellWidth + cellWidth / 2 - dWidth / 2;
    const cy = y * cellHeight + cellHeight / 2 - dHeight / 2;

    // Coordinates for the text
    const tx = (x + 0.5) * cellWidth;
    const ty = (y + 0.5) * cellHeight;

    img.onload = function () {
      context.drawImage(img, cx, cy, dWidth, dHeight);
      // This part draws the text on the image
      if (text !== undefined) {
        // ToDo: Fix fillStyle
        // context.fillStyle = text_color;
        context.textAlign = "center";
        context.textBaseline = "middle";
        context.fillText(text, tx, ty);
      }
    };
  };

  /**
        Draw Grid lines in the full gird
        */

  this.drawGridLines = function () {
    context.beginPath();
    context.strokeStyle = "#eee";
    maxX = cellWidth * gridWidth;
    maxY = cellHeight * gridHeight;

    // Draw horizontal grid lines:
    for (let y = 0; y <= maxY; y += cellHeight) {
      context.moveTo(0, y + 0.5);
      context.lineTo(maxX, y + 0.5);
    }

    for (let x = 0; x <= maxX; x += cellWidth) {
      context.moveTo(x + 0.5, 0);
      context.lineTo(x + 0.5, maxY);
    }

    context.stroke();
  };

  this.resetCanvas = function () {
    context.clearRect(0, 0, width, height);
    context.beginPath();
  };
};

const clamp = function (val, min, max) {
  return Math.min(Math.max(min, val), max);
}
