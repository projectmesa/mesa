import { controller } from "./controls.js";
import * as vizElements from "./viz-elements.js";
import { initGUI } from "./gui.js";

/** Open the websocket connection; support TLS-specific URLs when appropriate */
const ws = new WebSocket(
  (window.location.protocol === "https:" ? "wss://" : "ws://") +
    location.host +
    "/ws"
);

/**
 * Parse and handle an incoming message on the WebSocket connection.
 * @param {string} message - the message received from the WebSocket
 */
ws.onmessage = function(message) {
  const msg = JSON.parse(message.data);
  switch (msg["type"]) {
    case "viz_state":
      // Update visualization state
      vizElements.render(msg["data"]);
      break;
    case "end":
      // We have reached the end of the model
      controller.done();
      break;
    case "model_params":
      // Create GUI elements for each model parameter and reset everything
      initGUI(msg["params"]);
      controller.reset();
      break;
    case "elements":
      // Create visualization elements
      vizElements.add(msg["elements"]);
      break;
    default:
      // There shouldn't be any other message
      console.log("Unexpected message.");
      console.log(msg);
  }
};

/**
 * Turn an object into a string to send to the server, and send it.
 * @param {string} message - The message to send to the Python server
 */
export const send = function(message) {
  const msg = JSON.stringify(message);
  ws.send(msg);
};
