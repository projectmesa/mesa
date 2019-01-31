import { send } from "./websocket.js";
import { elements } from "./main.js";

class ModelController {
  constructor() {
    this.tick = 0;
    this.fps = 3;
    this.running = false;
    this.finished = false;
    this.player = 0;
  }

  start() {
    this.running = true;
    this.player = setInterval(() => this.step(), 1000 / this.fps);
    startModelButton.innerText = "Stop";
  }

  stop() {
    this.running = false;
    clearInterval(this.player);
    startModelButton.innerText = "Start";
  }

  step() {
    this.tick += 1;
    send({ type: "get_step", step: this.tick });
    stepDisplay.innerText = this.tick;
  }

  reset() {
    this.tick = 0;
    stepDisplay.innerText = this.tick;
    send({ type: "reset" });
    // Reset all the visualizations
    for (var i in elements) {
      elements[i].reset();
    }
    this.finished = false;
    if (!this.running) {
      startModelButton.innerText = "Start";
    }
  }

  done() {
    this.stop();
    this.finished = true;
    startModelButton.innerText = "Done";
  }
}

export const controller = new ModelController();

const stepDisplay = document.getElementById("step");

const startModelButton = document.getElementById("startModel");
startModelButton.onclick = () => {
  if (controller.running) {
    controller.stop();
  } else if (!controller.finished) {
    controller.start();
  }
};

const stepModelButton = document.getElementById("stepModel");
stepModelButton.onclick = () => {
  if (!controller.running & !controller.finished) {
    controller.step();
  }
};

const resetModelButton = document.getElementById("resetModel");
resetModelButton.onclick = () => controller.reset();
