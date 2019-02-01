import { send } from "./websocket.js";

const onSubmitCallback = function(param_name, value) {
  send({ type: "submit_params", param: param_name, value: value });
};

export const addBooleanInput = function(param, obj) {
  var domID = param + "_id";
  sidebar.insertAdjacentHTML(
    "beforeend",
    [
      "<div class='input-group input-group-lg'>",
      "<p><label for='" +
        domID +
        "' class='label label-primary'>" +
        obj.name +
        "</label></p>",
      "<input class='model-parameter' id='" + domID + "' type='checkbox'/>",
      "</div>"
    ].join("")
  );
  $("#" + domID).bootstrapSwitch({
    state: obj.value,
    size: "small",
    onSwitchChange: function(e, state) {
      onSubmitCallback(param, state);
    }
  });
};

export const addNumberInput = function(param, obj) {
  var domID = param + "_id";
  sidebar.insertAdjacentHTML(
    "beforeend",
    [
      "<div class='input-group input-group-lg'>",
      "<p><label for='" +
        domID +
        "' class='label label-primary'>" +
        obj.name +
        "</label></p>",
      "<input class='model-parameter' id='" + domID + "' type='number'/>",
      "</div>"
    ].join("")
  );
  var numberInput = $("#" + domID);
  numberInput.val(obj.value);
  numberInput.on("change", function() {
    onSubmitCallback(param, Number($(this).val()));
  });
};

export const addSliderInput = function(param, obj) {
  var domID = param + "_id";
  var tooltipID = domID + "_tooltip";
  sidebar.insertAdjacentHTML(
    "beforeend",
    [
      "<div class='input-group input-group-lg'>",
      "<p>",
      "<a id='" +
        tooltipID +
        "' data-toggle='tooltip' data-placement='top' class='label label-primary'>",
      obj.name,
      "</a>",
      "</p>",
      "<input id='" + domID + "' type='text' />",
      "</div>"
    ].join("")
  );

  // Enable tooltip label
  if (obj.description !== null) {
    $(tooltipID).tooltip({
      title: obj.description,
      placement: "right"
    });
  }

  // Setup slider
  var sliderInput = $("#" + domID);
  sliderInput.slider({
    min: obj.min_value,
    max: obj.max_value,
    value: obj.value,
    step: obj.step,
    ticks: [obj.min_value, obj.max_value],
    ticks_labels: [obj.min_value, obj.max_value],
    ticks_positions: [0, 100]
  });
  sliderInput.on("change", function() {
    onSubmitCallback(param, Number($(this).val()));
  });
};

export const addChoiceInput = function(param, obj) {
  var domID = param + "_id";
  var span = "<span class='caret'></span>";
  var template = [
    "<p><label for='" +
      domID +
      "' class='label label-primary'>" +
      obj.name +
      "</label></p>",
    "<div class='dropdown'>",
    "<button id='" +
      domID +
      "' class='btn btn-default dropdown-toggle' type='button' data-toggle='dropdown'>" +
      obj.value +
      " " +
      span,
    "</button>",
    "<ul class='dropdown-menu' role='menu' aria-labelledby='" + domID + "'>"
  ];
  var choiceIdentifiers = [];
  for (var i = 0; i < obj.choices.length; i++) {
    var choiceID = domID + "_choice_" + i;
    choiceIdentifiers.push(choiceID);
    template.push(
      "<li role='presentation'><a class='pick-choice' id='" +
        choiceID +
        "' role='menuitem' tabindex='-1' href='#'>",
      obj.choices[i],
      "</a></li>"
    );
  }

  // Close the dropdown options
  template.push("</ul>", "</div>");

  // Finally render the dropdown and activate choice listeners
  sidebar.insertAdjacentHTML("beforeend", template.join(""));
  choiceIdentifiers.forEach(function(id, idx) {
    $("#" + id).on("click", function() {
      var value = obj.choices[idx];
      $("#" + domID).html(value + " " + span);
      onSubmitCallback(param, value);
    });
  });
};

export const addTextBox = function(param, obj) {
  var well = $('<div class="well">' + obj.value + "</div>")[0];
  sidebar.insertAdjacentHTML("beforeend", well);
};

/** Alternative-style for creating a SliderInput
 * Not in use

const input_template = document.querySelector("template");

/** Add a slider input to the documents "input" section
 * @param {string} param - The id of the parameter
 * @param {object} obj - The object describing the slider

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
*/
