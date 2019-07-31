import { html, parent } from "../hybrids.min.js"
import AppStore from "./app-store.js"

/**
 * Input section for the individual Input Parameters
 * @typedef {object} InputParameters
 * @property {string[]} parameter - List of parameter names
 * @property {string} render - Mapping of names to mesa inputs
 */
export const InputParameters = {
  store: parent(AppStore),
  parameter: ({ store }) => Object.keys(store.parameter),
  render: ({ parameter }) => html`
    <h2>Input Parameters</h2>
    ${parameter.map(
      param => html`
        <mesa-input paramName=${param}></mesa-input>
      `
    )}
  `
}

/**
 * @typedef {object} MesaInput
 * @property {AppStore} store - app-store element instance
 * @property {string} paramName - name of the parameter
 * @property {Parameter} parameter - user-settable input parameter
 */
export const MesaInput = {
  store: parent(AppStore),
  paramName: "",
  parameter: ({ store, paramName }) => store.parameter[paramName],
  render: ({ parameter }) => html`
    <wl-expansion>
      <span slot="title">${parameter.options.name}</span>
      <span slot="description">${parameter.currentValue}</span>
      ${addInput(parameter)}
    </wl-expansion>
  `
}

/**
 * Create input elements based on the type of the input parameter
 * @param {Parameter} parameter - Input parameter
 */
function addInput(parameter) {
  let type = parameter.type
  let options = parameter.options
  let currentValue = parameter.currentValue
  let model_values = parameter.options.model_values
  switch (type) {
    case "slider":
      return html`
        ${model_values.map(
          (value, index) => html`
            <wl-slider
              thumbLabel
              min=${options.min_value}
              max=${options.max_value}
              step=${options.step}
              buffervalue=${currentValue}
              oninput=${changeValue.bind(index)}
              label=${value}
            >
              <span slot="before">${options.min_value}</span>
              <span slot="after">${options.max_value}</span>
            </wl-slider>
          `
        )}
      `
    case "number":
      return html`
        <wl-textfield
          type="number"
          min=${options.min_value}
          max=${options.max_value}
          step=${options.step}
          value=${options.value}
          oninput=${changeValue}
        ></wl-textfield>
      `
    case "choice":
      return html`
        ${model_values.map(
          (value, index) => html`
            <wl-select oninput=${changeValue.bind(index)}>
              ${options.choices.map(
                option =>
                  html`
                    <option>${option}</option>
                  `
              )}
            </wl-select>
          `
        )}
      `
    case "checkbox":
      return html`
        ${options.value
          ? html`
              <wl-switch checked></wl-switch>
            `
          : html`
              <wl-switch></wl-switch>
            `}
      `
    case "static_text":
      return html`
        <wl-text>${options.value}</wl-text>
      `

    default:
      console.log("Unexpected parameter type:")
      console.log(type)
  }
}

/**
 * Change input parameter value in the store
 * @param {InputElement} host - mesa-input instance
 * @param {Event} event - input event
 */
function changeValue({ store, paramName }, event) {
  let value = event.target.value
  send({
    type: "submit_params",
    data: {
      model: this,
      param: paramName,
      value: Number(value) || value
    }
  })
  store.parameter = {
    ...store.parameter,
    [paramName]: {
      ...store.parameter[paramName],
      options: {
        ...store.parameter[paramName].options,
        value: value
      }
    }
  }
}
