import { html, parent, render } from "../hybrids.min.js"
import AppStore from "./app-store.js"

const VegaElements = {
  store: parent(AppStore),
  specs: ({ store }) => store.specs,
  sims: ({ store }) => [...Array(store.n_simulations).keys()],
  render: render(
    ({ specs, sims }) => html`
      ${sims.map(
        n => html`
          <div class="model" id="model${n}">
            ${specs.map(
              (_, index) => html`
                <div id="view${index}"></div>
              `
            )}
          </div>
        `
      )}
    `,
    { shadowRoot: false }
  )
}

export default VegaElements
