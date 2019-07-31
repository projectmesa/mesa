import { property } from "../hybrids.min.js"

/**
 * Main AppStore for saving state across the Application
 * @typedef {Object} AppStore
 * @property {number} steps - The current model step
 * @property {boolean} running - Should the model continously update
 * @property {boolean} done - Whether the model is in a running state
 * @property {Parameter[]} parameter - User-settable parameters
 * @property {boolean} rendered - Is the current visualization state rendered
 * @property {number} timeout - the current timeout for step changes
 */
const AppStore = {
  currentStep: { observe: sendStep },
  maxStep: 0,
  running: false,
  n_simulations: 1,
  done: false,
  parameter: [],
  specs: [],
  views: ({ specs }) => createViews(specs),
  model_state: {
    ...property([]),
    observe: updateViews
  },
  fps: 3,
  timeout: 0
}

export default AppStore

function createViews(specs) {
  let models = [...document.querySelectorAll(".model")]
  let views = models.map(model =>
    [...model.children].map(async (view_container, index) => {
      let result = await vegaEmbed(view_container, specs[index], {
        patch: {
          signals: [
            {
              name: "get_datum",
              on: [
                {
                  events: "click, mousemove[event.buttons]",
                  update: "datum"
                }
              ]
            }
          ]
        }
      })
      result.view.addSignalListener(
        "get_datum",
        sendSignal.bind(result.view.container())
      )
      return result
    })
  )
  return views
}

/**
 * React to changes in the step counter - by resetting or getting the next step.
 * @param {AppStore} store - The application store
 */
function sendStep(store) {
  send({ type: "get_state", data: { step: store.currentStep } })
}

const sendSignal = function(name, value = {}) {
  let model_id = parseInt(this.parentElement.id.slice(5))
  send({
    type: "call_method",
    data: {
      step: store.currentStep,
      model_id: model_id,
      data: value
    }
  })
  send({
    type: "get_state",
    data: {
      step: store.currentStep
    }
  })
}

export async function updateViews(store, data) {
  data.forEach((modelData, index) => {
    let { agents, ...model } = modelData
    let agentChange = vega
      .changeset()
      .insert(agents)
      .remove(vega.truthy)
    store.views[index].map(async aview => {
      let result = await aview
      let view = result.view
      let datasets = view.getState({
        data: vega.truthy
      }).data
      if ("agents" in datasets) {
        view.change("agents", agentChange)
      }
      if ("model" in datasets) {
        view.insert("model", model)
      }
      view.runAsync()
    })
  })
}
