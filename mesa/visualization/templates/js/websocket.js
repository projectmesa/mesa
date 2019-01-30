import { control, reset, player } from "./controls.js";
import { elements, initGUI } from "./main.js";

// Open the websocket connection; support TLS-specific URLs when appropriate
const ws = new WebSocket(
  (window.location.protocol === "https:" ? "wss://" : "ws://") +
    location.host +
    "/ws"
);

ws.onopen = function() {
  console.log("Connection opened!");
  send({ type: "get_params" }); // Request model parameters when websocket is ready
  reset();
};

/** Parse and handle an incoming message on the WebSocket connection. */
ws.onmessage = function(message) {
  let msg = JSON.parse(message.data);
  switch (msg["type"]) {
    case "viz_state":
      const data = msg["data"];
      for (let i in elements) {
        elements[i].render(data[i]);
      }
      break;
    case "end":
      // We have reached the end of the model
      control.running = false;
      control.done = true;
      console.log("Done!");
      clearInterval(player);
      $(playPauseButton.children()[0]).text("Done");
      break;
    case "model_params":
      console.log(msg["params"]);
      let model_params = msg["params"];
      initGUI(model_params);
      break;
    case "elements":
      console.log(msg["elements"]);
      msg["elements"].forEach(elem => eval(elem));
      break;
    default:
      // There shouldn't be any other message
      console.log("Unexpected message.");
      console.log(msg);
  }
};

/**	 Turn an object into a string to send to the server, and send it. v*/
export const send = function(message) {
  let msg = JSON.stringify(message);
  ws.send(msg);
};
