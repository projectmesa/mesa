import { send } from "./websocket.js";

const input_template = document.querySelector("template");

var onSubmitCallback = function(param_name, value) {
  send({ type: "submit_params", param: param_name, value: value });
};

/** Add a slider input to the documents "input" section
 * @param {string} param - The id of the parameter
 * @param {object} obj - The object describing the slider
 */
export const addSliderInput = function(param, obj) {
  const sliderNode = input_template.content.cloneNode(true);

  const title = sliderNode.getElementById("title");
  title.innerText = obj.name;

  const input = sliderNode.querySelector("input");
  input.type = "range";
  input.min = obj.min_value;
  input.max = obj.max_value;
  input.value = obj.value;
  input.step = obj.step;
  input.id = param;

  const output = sliderNode.getElementById("value");
  output.innerText = input.value;

  input.oninput = function() {
    output.innerText = input.value;
    onSubmitCallback(param, Number(input.value));
  };
  document.getElementById("input").appendChild(sliderNode);
};
