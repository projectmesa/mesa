// import { html, define, parent } from "https://unpkg.com/hybrids/src"
var define = window.hybrids.define
var html = window.hybrids.html
var parent = window.hybrids.parent
var property = window.hybrids.property

const store = document.querySelector("app-store")
const vizElements = []

/** Open the websocket connection; support TLS-specific URLs when appropriate */
const ws = new window.WebSocket(
  (window.location.protocol === "https:" ? "wss://" : "ws://") +
    window.location.host +
    "/ws"
)
/**
 * Parse and handle an incoming message on the WebSocket connection.
 * @param {string} message - the message received from the WebSocket
 */
ws.onmessage = function(message) {
  const msg = JSON.parse(message.data)
  switch (msg.type) {
    case "viz_state":
      // Update visualization state
      window.control.tick = store.steps
      vizElements.forEach((element, index) => element.render(msg.data[index]))
      store.rendered = true
      break
    case "end":
      // We have reached the end of the model
      store.done = true
      store.running = false
      break
    case "reset":
      vizElements.forEach(element => element.reset())
      store.rendered = false
      break
    case "model_params":
      // Create GUI elements for each model parameter and reset everything
      msg.params.forEach(param => addParameter(store, param))
      break
    default:
      // There shouldn't be any other message
      console.log("Unexpected message.")
      console.log(msg)
  }
}
/**
 * Get the first step once the websocket is open
 */
ws.onopen = () => (store.steps = -1)

/**
 * Turn an object into a string to send to the server, and send it.
 * @param {string} message - The message to send to the Python server
 */
function send(message) {
  const msg = JSON.stringify(message)
  ws.send(msg)
}

/**
 * Create a default property with observe function attached.
 * @param {any} defaultValue - Defaultvalue for the parameter
 * @param {function} func - observe function to be called when value changes
 */
function observer(defaultValue = 0, func = () => sideEffects()) {
  const prop = property(defaultValue)
  prop.observe = func
  return prop
}

/**
 * Main Appstore for saving state accross the Application
 * @typedef {Object} AppStore
 * @property {number} steps - The current model step
 * @property {boolean} running - Should the model continously update
 * @property {boolean} done - Whether the model is in a running state
 * @property {InputParameter[]} parameter - User-settable parameters
 * @property {boolean} rendered - Is the current visualization state rendered
 * @property {number} timeout - the current timeout for step changes
 */
const AppStore = {
  steps: { observe: sendStep },
  running: observer(false, runModel),
  done: false,
  parameter: [],
  fps: 3,
  rendered: observer(false, runModel),
  timeout: 0
}

/**
 * React to changes in the step counter - by resetting or getting the next step.
 * @param {AppStore} store - The application store
 */
function sendStep(store) {
  if (store.steps < 0) {
    send({ type: "reset" })
    store.timeout = setTimeout(incrementStep, 1, {
      store: store
    })
  } else {
    send({ type: "get_step", step: store.steps })
  }
}

/**
 * Host object connected to an AppStore.
 * @typedef {Object} Host
 * @property {AppStore} store - The main application store

/**
 * Increment model steps by one.
 * @param {Host} host - an element instance
 */
function incrementStep({ store }) {
  if (!store.done) {
    store.rendered = false
    store.steps += 1
  }
}

/**
 * Toggle the models running state.
 * @param {Host} host - an element instance
 */
function toggleRunning({ store }) {
  clearTimeout(store.timeout)
  if (!store.done) {
    store.running = !store.running
  }
}

/**
 * Schedule next step if visualiztion is rendered and model is running
 * @param {AppStore} store - The application store
 */
function runModel(store) {
  if (store.rendered && store.running) {
    store.timeout = setTimeout(incrementStep, 1000 / store.fps, {
      store: store
    })
  }
}

/**
 * Reset the model
 * @param {Host} param0 - an element instance
 */
function resetModel({ store }) {
  clearTimeout(store.timeout)
  store.rendered = false
  store.done = false
  store.steps = -1
}

const AppControl = {
  store: parent(AppStore),
  isRunning: ({ store }) => store.running,
  labelStartStop: ({ isRunning }) => (isRunning ? "Stop" : "Start"),
  render: ({ isRunning, labelStartStop }) => html`
    <wl-button onclick=${toggleRunning}>${labelStartStop}</wl-button>
    ${isRunning
      ? html`
          <wl-button disabled onclick=${incrementStep}> Step</wl-button>
        `
      : html`
          <wl-button onclick=${incrementStep}> Step</wl-button>
        `}
    <wl-button onclick=${resetModel}>Reset</wl-button>
  `
}

window.store = document.querySelector("app-store")

function addParameter(store, param) {
  store.parameter = {
    ...store.parameter,
    [param.parameter]: {
      currentValue: param.value,
      type: param.param_type,
      options: param
    }
  }
}

/**
 * Change input parameter value
 * @param {InputElement} host - mesa-input instance
 * @param {Event} event - input event
 */
function changeValue({ store, paramName }, event) {
  console.log(event)
  send({
    type: "submit_params",
    param: paramName,
    value: Number(event.target.value) || event.target.value
  })

  store.parameter = {
    ...store.parameter,
    [paramName]: {
      ...store.parameter[paramName],
      options: {
        ...store.parameter[paramName].options,
        value: event.target.value
      }
    }
  }
}

const InputParameters = {
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
 * @typedef {object} InputElement
 * @property {AppStore} store - app-store element instance
 * @property {string} paramName - name of the parameter
 * @property {InputParameter} parameter - user-settable input parameter
 */
const Input = {
  store: parent(AppStore),
  paramName: "",
  parameter: ({ store, paramName }) => store.parameter[paramName],
  type: ({ parameter }) => parameter.type,
  options: ({ parameter }) => parameter.options,
  currentValue: ({ parameter }) => parameter.currentValue,
  render: ({ type, options, currentValue }) => html`
    <wl-expansion>
      <span slot="title">${options.name}</span>
      <span slot="description">${currentValue}</span>
      ${addInput(type, options, currentValue)}
    </wl-expansion>
  `
}

function addInput(type, options, currentValue) {
  switch (type) {
    case "slider":
      return html`
        <wl-slider
          thumbLabel
          min=${options.min_value}
          max=${options.max_value}
          step=${options.step}
          buffervalue=${currentValue}
          oninput=${changeValue}
          label=${options.value}
        >
          <span slot="before">${options.min_value}</span>
          <span slot="after">${options.max_value}</span>
        </wl-slider>
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
        <wl-select oninput=${changeValue}>
          ${options.choices.map(
            option =>
              html`
                <option>${option}</option>
              `
          )}
        </wl-select>
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
      console.log("unexpected parameter type:")
      console.log(type)
  }
}

const fpsControl = {
  store: parent(AppStore),
  currentStep: ({ store }) => (store.steps < 0 ? 0 : store.steps),
  fps: ({ store }) => store.fps,
  render: ({ currentStep, fps }) => html`
    <style>
      wl-text {
        margin-left: 8px;
      }
      :host {
        display: flex;
        align-items: center;
      }
    </style>
    <wl-slider
      min="0"
      max="25"
      step="1"
      value=${fps}
      oninput=${updateFPS}
      label="FPS Control"
      thumbLabel
    >
    </wl-slider>
    <wl-text slot="left">Current Step: ${currentStep}</wl-text>
  `
}

function updateFPS({ store }, { target }) {
  store.fps = target.value
}

define("app-store", AppStore)
define("app-control", AppControl)
define("mesa-input", Input)
define("input-parameters", InputParameters)
define("fps-control", fpsControl)

window.elements = vizElements
window.control = { tick: store.steps }
