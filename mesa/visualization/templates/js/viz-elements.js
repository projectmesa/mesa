import { send } from "./websocket.js";
import { controller } from "./controls.js";

export const vizElements = [];

// All current Visualization modules use elements instead of vizElements
const elements = vizElements;

/**
 * Add visualization elements
 * @param {Array<string>} newElements - JS code that creates visualization elements
 */
export const add = function(newElements) {
  newElements.forEach(element => eval(element));
};

/**
 * Update elements state
 * @param {number} step - The step to visualize
 */
export const update = function(step) {
  send({ type: "get_step", step: step });
  // The response will trigger this modules render function
};

/**
 * Render each element with the incoming data
 * @param {object} data - data provided for the visualization elements
 */
export const render = function(data) {
  for (let i in vizElements) {
    vizElements[i].render(data[i]);
  }
  if (controller.running) {
    setTimeout(() => controller.step(), 1000 / controller.fps);
  }
};

/** Reset the visualization state of each element */
export const reset = function() {
  for (let i in vizElements) {
    vizElements[i].reset();
  }
};
