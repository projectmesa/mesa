import { send } from "./websocket.js";

export const elements = [];
export let rendered = false;

export const add = function(element) {
  element.forEach(elem => eval(elem));
};

export const update = function(tick) {
  send({ type: "get_step", step: tick });
  rendered = false;
};

export const render = function(data) {
  for (let i in elements) {
    elements[i].render(data[i]);
  }
  rendered = true;
};

export const reset = function() {
  for (let i in elements) {
    elements[i].reset();
  }
};
