export const elements = [];

export const add = function(element) {
  element.forEach(elem => eval(elem));
};

export const render = function(data) {
  for (let i in elements) {
    elements[i].render(data[i]);
  }
};

export const reset = function() {
  for (let i in elements) {
    elements[i].reset();
  }
};
