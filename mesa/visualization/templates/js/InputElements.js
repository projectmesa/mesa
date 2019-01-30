import { send } from "./websocket.js";

const temp = document.querySelector("template")

var onSubmitCallback = function (param_name, value) {
  send({"type": "submit_params", "param": param_name, "value": value});
};

export const addSliderInput = function (param, obj) {
  const sliderNode = temp.content.cloneNode(true);

  const title = sliderNode.getElementById("title");
  title.innerHTML = obj.name

  const input = sliderNode.querySelector("input");
  input.type = "range";
  input.min = obj.min_value;
  input.max = obj.max_value;
  input.value = obj.value;
  input.step = obj.step;
  input.id = param;

  const output = sliderNode.getElementById("value");
  output.innerHTML = input.value;



  input.oninput = function () {
    output.innerHTML = input.value;
    onSubmitCallback(param, Number(input.value));
  };
  document.getElementById("input").appendChild(sliderNode);
};
