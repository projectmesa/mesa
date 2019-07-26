import { define } from "./hybrids.min.js"
import AppStore from "./elements/app-store.js"
import {
  AppControl,
  FPSControl,
  incrementStep
} from "./elements/app-control.js"
import VegaElements from "./elements/vega-elements.js"
import { InputParameters, MesaInput } from "./elements/mesa-input.js"

// Define custom elements
define("app-store", AppStore)
define("app-control", AppControl)
define("input-parameters", InputParameters)
define("mesa-input", MesaInput)
define("fps-control", FPSControl)
define("vega-elements", VegaElements)

// Set-up reference to the actual app store instance
const store = document.querySelector("app-store")

/** Open the websocket connection; support TLS-specific URLs when appropriate */
const ws = new window.WebSocket(
  (window.location.protocol === "https:" ? "wss://" : "ws://") +
    window.location.host +
    "/ws"
)

/**
 * Turn an object into a string to send to the server, and send it.
 * @param {string} message - The message to send to the Python server
 */

function send(message) {
  const msg = JSON.stringify(message)
  ws.send(msg)
}

/**
 * reset the model once the websocket is open
 */
ws.onopen = () => {
  send({ type: "reset", data: {} })
  store.currentStep = 0
}

/**
 * Parse and handle an incoming message on the WebSocket connection.
 * @param {string} message - the message received from the WebSocket
 */
ws.onmessage = function(message) {
  const msg = JSON.parse(message.data)
  switch (msg.type) {
    case "model_state":
      // Update visualization state
      store.model_state = msg.data.map(state => JSON.parse(state))
      // Workaround to display timeline correctly (but delayed)
      document
        .querySelector("fps-control")
        .shadowRoot.querySelector("#timeline").value = store.currentStep
      // Init next step if model is running
      if (store.running) {
        store.timeout = setTimeout(incrementStep, 1000 / store.fps, {
          store: store
        })
      }
      break
    case "end":
      // We have reached the end of the model
      store.done = true
      store.running = false
      break
    case "model_params":
      // Create input elements for each model parameter
      msg.params.forEach(param => addParameter(store, param))
      break
    case "vega_specs":
      let specifications = msg.data.map(spec => JSON.parse(spec))
      store.specs = specifications
      store.n_simulations = msg.n_sims
      break
    default:
      // There shouldn't be any other message
      console.log("Unexpected message.")
      console.log(msg)
  }
}

/**
 * Add user-settable parameters to the input section.
 * @param {AppStore} store - element instance of the app store
 * @param {Parameter} param - raw parameter input from the Model Server
 */
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
 * Check which values have changed and send them to the model server
 * @param {AppStore} store - store element instance
 * @param {Parameter[]} value - new values of the parameters
 * @param {Parameter[]} lastValue - old values of the parameters
 */
function sendParameter(store, value, lastValue = []) {
  Object.keys(lastValue).forEach(param => {
    if (value[param].options.value != lastValue[param].options.value) {
      send({
        type: "submit_params",
        data: {
          model: this.model,
          param: param,
          value:
            Number(value[param].options.value) || value[param].options.value
        }
      })
    }
  })
}

window.store = store
window.send = send
