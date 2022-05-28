const CanvasHexModule = function (
  canvas_width,
  canvas_height,
  grid_width,
  grid_height
) {
  const createElement = (tagName, attrs) => {
    const element = document.createElement(tagName);
    Object.assign(element, attrs);
    return element;
  };

  // Create the element
  // ------------------
  const parent = createElement("div", {
    style: `height:${canvas_height}px;`,
    className: "world-grid-parent",
  });

  // Create the tag with absolute positioning :
  const createCanvas = () => {
    const el = createElement("canvas", {
      width: canvas_width,
      height: canvas_height,
      className: "world-grid",
    });
    return el;
  };
  const canvas = createCanvas();
  const interaction_canvas = createCanvas();

  // Append it to parent:
  parent.appendChild(canvas);
  parent.appendChild(interaction_canvas);

  // Append it to #elements
  const elements = document.getElementById("elements");
  elements.appendChild(parent);

  // Create the context and the drawing controller:
  const context = canvas.getContext("2d");

  const interactionHandler = new InteractionHandler(
    canvas_width,
    canvas_height,
    grid_width,
    grid_height,
    interaction_canvas.getContext("2d")
  );

  const canvasDraw = new HexVisualization(
    canvas_width,
    canvas_height,
    grid_width,
    grid_height,
    context,
    interactionHandler
  );

  this.render = (data) => {
    canvasDraw.resetCanvas();
    for (const layer in data) canvasDraw.drawLayer(data[layer]);
    canvasDraw.drawGridLines("#eee");
  };

  this.reset = () => {
    canvasDraw.resetCanvas();
  };
};
