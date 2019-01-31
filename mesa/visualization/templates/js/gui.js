import { addSliderInput } from "./InputElements.js";

export const initGUI = function(model_params) {
  var addParamInput = function(param, option) {
    switch (option["param_type"]) {
      case "checkbox":
        addBooleanInput(param, option);
        break;

      case "slider":
        addSliderInput(param, option);
        break;

      case "choice":
        addChoiceInput(param, option);
        break;

      case "number":
        addNumberInput(param, option); // Behaves the same as just a simple number
        break;

      case "static_text":
        addTextBox(param, option);
        break;
    }
  };

  for (var option in model_params) {
    var type = typeof model_params[option];
    var param_str = String(option);

    switch (type) {
      case "boolean":
        addBooleanInput(param_str, {
          value: model_params[option],
          name: param_str
        });
        break;
      case "number":
        addNumberInput(param_str, {
          value: model_params[option],
          name: param_str
        });
        break;
      case "object":
        addParamInput(param_str, model_params[option]); // catch-all for params that use Option class
        break;
    }
  }
};
