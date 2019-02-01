import { send } from "./websocket.js";
import * as elements from "./elements.js";

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
    startModelButton.firstElementChild.innerText = "Stop";
  }

  stop() {
    this.running = false;
    clearInterval(this.player);
    startModelButton.firstElementChild.innerText = "Start";
  }

  step() {
    this.tick += 1;
    stepDisplay.innerText = this.tick;
    send({ type: "get_step", step: this.tick });
  }

  reset() {
    this.tick = 0;
    stepDisplay.innerText = this.tick;
    send({ type: "reset" });
    // Reset all the visualizations
    elements.reset()
    if (this.finished) {
      this.finished = false;
      startModelButton.firstElementChild.innerText = "Start";
    }
  }

  done() {
    this.stop();
    this.finished = true;
    startModelButton.firstElementChild.innerText = "Done";
  }

  updateFPS(val) {
    this.fps = Number(val);
    if (this.running) {
      this.stop();
      this.start();
    }
  }
}

export const controller = new ModelController();

const stepDisplay = document.getElementById("step");

const fpsControl = $("#fps").slider({
  max: 20,
  min: 0,
  value: 3,
  ticks: [0, 20],
  ticks_labels: [0, 20],
  ticks_position: [0, 100]
});
fpsControl.on('change', () => controller.updateFPS(fpsControl.val()))

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
