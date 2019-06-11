// import { html, define, parent } from "https://unpkg.com/hybrids/src"
var define = window.hybrids.define
var html = window.hybrids.html
var parent = window.hybrids.parent

const store = document.querySelector("app-store")
const vizElements = []

/** Open the websocket connection; support TLS-specific URLs when appropriate */
const ws = new window.WebSocket(
  (window.location.protocol === "https:" ? "wss://" : "ws://") +
    window.location.host +
    "/ws"
)

window.test = store
window.toggle = toggleRunning

/**
 * Parse and handle an incoming message on the WebSocket connection.
 * @param {string} message - the message received from the WebSocket
 */
ws.onmessage = function(message) {
  const msg = JSON.parse(message.data)
  console.log(msg)
  switch (msg.type) {
    case "viz_state":
      // Update visualization state
      vizElements.forEach((element, index) => element.render(msg.data[index]))
      break
    case "end":
      // We have reached the end of the model
      // controller.done()
      break
    case "model_params":
      // Create GUI elements for each model parameter and reset everything
      initGUI(msg.params)
      break
    default:
      // There shouldn't be any other message
      console.log("Unexpected message.")
      console.log(msg)
  }
}

/**
 * Turn an object into a string to send to the server, and send it.
 * @param {string} message - The message to send to the Python server
 */
const send = function(message) {
  const msg = JSON.stringify(message)
  ws.send(msg)
}

function initGUI(params) {
  console.log(params)
  const sidebar = document.getElementById("sidebar")
  Object.keys(params).forEach(name => {
    let options = params[name]
    addParameter(window.store, name, options.value, options.param_type, options)
  })
}

const AppStore = {
  steps: {
    observe: sendStep
  },
  running: {
    observe: runModel
  },
  parameter: [],
  fps: 3
}

function sendStep({ steps }) {
  send({ type: "get_step", step: steps })
}

const SocketHandler = {}

function changeStep({ store }, { target = { value: 1 } } = {}) {
  store.steps += Number(target.value)
}

function toggleRunning({ store }) {
  store.running = !store.running
}

function runModel(store) {
  if (store.running) {
    changeStep({ store })
    setTimeout(runModel, 1000 / store.fps, store)
  }
}

function resetModel({ store }) {
  send({ type: "reset" })
  vizElements.forEach((element, index) => element.reset())
  store.steps = 0
}

const AppControl = {
  store: parent(AppStore),
  labelStartStop: ({ store }) => (store.running ? "Stop" : "Start"),
  render: ({ labelStartStop }) => html`
    <wl-button onclick=${toggleRunning}>${labelStartStop}</wl-button>
    <wl-button onclick=${changeStep} value="1">Step</wl-button>
    <wl-button onclick=${resetModel}>Reset</wl-button>
  `
}
define("app-store", AppStore)
define("app-control", AppControl)

window.store = document.querySelector("app-store")
window.store.steps = 0

function addParameter(store, name, value, type, options) {
  store.parameter = {
    ...store.parameter,
    [name]: { currentValue: value, type: type, options: options }
  }
}

function changeValue({ store, paramName }, event) {
  send({
    type: "submit_params",
    param: paramName,
    value: Number(event.target.value)
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
          oninput=${changeValue}
        ></wl-textfield>
      `

    case "choice":
      return html`
        <wl-select>
          ${options.choices.map(
            option =>
              html`
                <option>${option}</option>
              `
          )}
        </wl-select>
      `

    default:
      console.log(type)
  }
}

function updateFPS({ store }, { target }) {
  store.fps = target.value
}

const fpsControl = {
  store: parent(AppStore),
  fps: ({ store }) => store.fps,
  render: ({ store, fps }) => html`
    <style>
      wl-text {
        margin-right: 8px;
      }
      :host {
        display: flex;
        align-items: center;
      }
    </style>
    <wl-text slot="left">Current Step: ${store.steps}</wl-text>
    <wl-slider oninput=${updateFPS} label="FPS Control" thumbLabel> </wl-slider>
  `
}

define("mesa-input", Input)
define("input-parameters", InputParameters)
define("fps-control", fpsControl)

window.elements = vizElements
window.control = { tick: store.steps }
