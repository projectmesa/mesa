import { send } from "./websocket.js"
import {elements} from "./main.js"

export const control = {
  tick: -1,
  running: false,
  done: false,
  fps: 3
};

const stepDisplay = document.getElementById("step");

Object.defineProperty(control, "step", {
  get: function() {
    return this.tick;
  },
  set: function(val) {
    this.tick = val;
    stepDisplay.innerText = val;
  }
});

control.step = 0;

export var player;

/** Send a message to the server get the next visualization state. */
const single_step = function() {
  control.step += 1;
  send({"type": "get_step", "step": control.tick});
};

/** Step the model forward. */
const step = function() {
  if (!control.running & !control.done) {
    single_step();
  } else if (!control.done) {
    run();
  }
};

const run = function() {
  if (control.running) {
    control.running = false;
    clearInterval(player);
    startModelButton.innerText = "Start";
  } else if (!control.done) {
    control.running = true;
    player = setInterval(single_step, 1000 / control.fps);
    startModelButton.innerText = "Stop";
  }
};

export const reset = function() {
    control.tick = 0;
    send({"type": "reset"});
    // Reset all the visualizations
    for (var i in elements) {
        elements[i].reset();
    }
  control.done = false;
  control.step = 0;
  if (!control.running) startModelButton.innerText = "Start";
};


const startModelButton = document.getElementById("startModel");
startModelButton.onclick = run;

const stepModelButton = document.getElementById("stepModel");
stepModelButton.onclick = function() {
  if (!control.running & !control.done) {
    single_step();
  } else if (!control.done) {
    run();
  }
};

const resetModelButton = document.getElementById("resetModel");
resetModelButton.onclick = reset