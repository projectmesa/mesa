/**
Mesa Visualization InteractionHandler
====================================================================

This uses the context of an additional canvas laid overtop of another canvas
visualization and maps mouse movements to agent position, displaying any agent
attributes included in the portrayal that are not listed in the ignoredFeatures.

The following portrayal will yield tooltips with wealth, id, and pos:

portrayal = {
   "Shape": "circle",
   "Filled": "true",
   "Layer": 0,
   "Color": colors[agent.wealth] if agent.wealth < len(colors) else '#a0a',
   "r": 0.3 + 0.1 * agent.wealth,
   "wealth": agent.wealth,
   "id": agent.unique_id,
   'pos': agent.pos
}

**/

const InteractionHandler = function (width, height, gridWidth, gridHeight, ctx) {
  // Find cell size:
  const cellWidth = Math.floor(width / gridWidth);
  const cellHeight = Math.floor(height / gridHeight);

  const lineHeight = 10;

  // list of standard rendering features to ignore (and key-values in the portrayal will be added )
  const ignoredFeatures = [
    "Shape",
    "Filled",
    "Color",
    "r",
    "x",
    "y",
    "xAlign",
    "yAlign",
    "w",
    "h",
    "width",
    "height",
    "heading_x",
    "heading_y",
    "stroke_color",
    "text_color",
  ];

  // Set a variable to hold the lookup table and make it accessible to draw scripts
  const mouseoverLookupTable = (this.mouseoverLookupTable = buildLookupTable(
    gridWidth,
    gridHeight
  ));
  function buildLookupTable(gridWidth, gridHeight) {
    let lookupTable;
    this.init = function () {
      lookupTable = [...Array(gridHeight).keys()].map((i) => Array(gridWidth));
    };

    this.set = function (x, y, value) {
      if (lookupTable[y][x]) lookupTable[y][x].push(value);
      else lookupTable[y][x] = [value];
    };

    this.get = function (x, y) {
      if (lookupTable[y]) return lookupTable[y][x] || [];
      return [];
    };

    return this;
  }

  let coordinateMapper;
  this.setCoordinateMapper = function (mapperName) {
    if (mapperName === "hex") {
      coordinateMapper = function (event) {
        const x = Math.floor(event.offsetX / cellWidth);
        const y =
          x % 2 === 0
            ? Math.floor(event.offsetY / cellHeight)
            : Math.floor((event.offsetY - cellHeight / 2) / cellHeight);
        return { x: x, y: y };
      };
      return;
    }

    // default coordinate mapper for grids
    coordinateMapper = function (event) {
      return {
        x: Math.floor(event.offsetX / cellWidth),
        y: Math.floor(event.offsetY / cellHeight),
      };
    };
  };

  this.setCoordinateMapper("grid");

  // wrap the rect styling in a function
  function drawTooltipBox(ctx, x, y, width, height) {
    ctx.fillStyle = "#F0F0F0";
    ctx.beginPath();
    ctx.shadowOffsetX = -3;
    ctx.shadowOffsetY = 2;
    ctx.shadowBlur = 6;
    ctx.shadowColor = "#33333377";
    ctx.rect(x, y, width, height);
    ctx.fill();
    ctx.shadowColor = "transparent";
  }

  let listener;
  let tmp;
  this.updateMouseListeners = function (portrayalLayer) {
    tmp = portrayalLayer;

    // Remove the prior event listener to avoid creating a new one every step
    ctx.canvas.removeEventListener("mousemove", listener);

    // define the event litser for this step
    listener = function (event) {
      // clear the previous interaction
      ctx.clearRect(0, 0, width, height);

      // map the event to x,y coordinates
      const position = coordinateMapper(event);
      const yPosition = Math.floor(event.offsetY / cellHeight);
      const xPosition = Math.floor(event.offsetX / cellWidth);

      // look up the portrayal items the coordinates refer to and draw a tooltip
      mouseoverLookupTable
        .get(position.x, position.y)
        .forEach((portrayalIndex, nthAgent) => {
          const agent = portrayalLayer[portrayalIndex];
          const features = Object.keys(agent).filter(
            (k) => ignoredFeatures.indexOf(k) < 0
          );
          const textWidth = Math.max.apply(
            null,
            features.map((k) => ctx.measureText(`${k}: ${agent[k]}`).width)
          );
          const textHeight = features.length * lineHeight;
          const y = Math.max(
            lineHeight * 2,
            Math.min(height - textHeight, event.offsetY - textHeight / 2)
          );
          const rectMargin = 2 * lineHeight;
          let x = 0;
          let rectX = 0;

          if (event.offsetX < width / 2) {
            x =
              event.offsetX + rectMargin + nthAgent * (textWidth + rectMargin);
            ctx.textAlign = "left";
            rectX = x - rectMargin / 2;
          } else {
            x =
              event.offsetX -
              rectMargin -
              nthAgent * (textWidth + rectMargin + lineHeight);
            ctx.textAlign = "right";
            rectX = x - textWidth - rectMargin / 2;
          }

          // draw a background box
          drawTooltipBox(
            ctx,
            rectX,
            y - rectMargin,
            textWidth + rectMargin,
            textHeight + rectMargin
          );

          // set the color and draw the text
          ctx.fillStyle = "black";
          features.forEach((k, i) => {
            ctx.fillText(`${k}: ${agent[k]}`, x, y + i * lineHeight);
          });
        });
    };
    ctx.canvas.addEventListener("mousemove", listener);
  };

  return this;
};
