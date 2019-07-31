import { html, parent } from "../hybrids.min.js"
import AppStore, { updateViews } from "./app-store.js"

/**
 * Control section to start/step/reset the model
 * @typedef {object} AppControl
 * @property {AppStore} store - element instance of the AppStore
 * @property {boolean} isRunning - Is the model in a running state
 * @property {string} labelStartStop - The label for the start/stop button
 * @property {string} render - How the three buttons appear
 */
export const AppControl = {
  store: parent(AppStore),
  isRunning: ({ store }) => store.running,
  labelStartStop: ({ isRunning }) => (isRunning ? "Stop" : "Start"),
  render: ({ isRunning, labelStartStop }) => html`
    <wl-button onclick=${toggleRunning}>${labelStartStop}</wl-button>
    <wl-button disabled="${isRunning}" onclick=${incrementStep}>
      Step</wl-button
    >
    <wl-button onclick=${resetModel}>Reset</wl-button>
  `
}

/**
 * Increment model steps by one.
 * @param {Host} host - an element instance
 */
export function incrementStep({ store }) {
  send({ type: "step", data: { step: store.currentStep + 1 } })
  store.currentStep += 1
  store.maxStep = store.currentStep
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
  if (store.running) {
    incrementStep({ store: store })
  }
}

/**
 * Reset the model
 * @param {Host} host - an element instance
 */
function resetModel({ store }) {
  clearTimeout(store.timeout)
  store.done = false
  send({ type: "reset", data: {} })
  resetViews(store)
  store.currentStep = 0
  store.maxStep = 0
  send({ type: "get_state", data: { step: 0 } })
}

/**
 * @typedef {object} FPSControl
 * @property {number} currentStep - The current model step
 * @property {number} fps - the current frames per second
 * @property {string} render - Display of current step and slider for FPS control
 */
export const FPSControl = {
  store: parent(AppStore),
  currentStep: ({ store }) => store.currentStep,
  maxStep: ({ store }) => store.maxStep,
  isRunning: ({ store }) => store.running,
  fps: ({ store }) => store.fps,
  render: ({ currentStep, fps, maxStep, isRunning }) => html`
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
    <wl-text slot="left">Timeline</wl-text>
    <wl-slider
      id="timeline"
      min="0"
      max=${maxStep}
      step="1"
      value=${currentStep}
      label="Current step: ${currentStep}"
      oninput=${getState}
      disabled="${isRunning}"
    >
      <wl-text slot="before">0</wl-text>
      <wl-text slot="after">${maxStep}</wl-text>
    </wl-slider>
  `
}

function getState({ store }, { target }) {
  let step = parseInt(target.value)
  store.currentStep = step
}

function updateFPS({ store }, { target }) {
  store.fps = target.value
}

function resetViews(store) {
  store.views.forEach(model =>
    model.forEach(aview =>
      aview.then(r => r.view.remove("model", vega.truthy).run())
    )
  )
}
