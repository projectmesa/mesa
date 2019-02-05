import { send } from "./websocket.js";

export const vizElements = [];
export let rendered = false;

// All current Visualization modules use elements instead of vizElements
const elements = vizElements;

/**
 * Add visualization elements
 * @param {string} element - JS code that is evaluated to create visualization elements
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
  rendered = false;
};

/**
 * Render each element with the incoming data
 * @param {object} data - data provided for the visualization elements
 */
export const render = function(data) {
  for (let i in vizElements) {
    vizElements[i].render(data[i]);
  }
  rendered = true;
};

/** Reset the visualization state of each element */
export const reset = function() {
  for (let i in vizElements) {
    vizElements[i].reset();
  }
};
