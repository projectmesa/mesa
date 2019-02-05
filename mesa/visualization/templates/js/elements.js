import { controller } from "./controls.js"

export const elements = [];

export const add = function(element) {
  element.forEach(elem => eval(elem));
};

export const render = function(data) {
  for (let i in elements) {
    elements[i].render(data[i]);
  }
  if (controller.running) {
    controller.player = setTimeout(() => controller.step(), 1000/controller.fps)
  }
};

export const reset = function() {
  for (let i in elements) {
    elements[i].reset();
  }
};
