import { send } from "./websocket.js";
import * as vizElements from "./viz-elements.js";

/** A ModelController class that controls the model state */
class ModelController {
  /**
   * Create a ModelController
   * @param  {number} tick=0 - Initial step of the model
   * @param  {number} fps=3 - Run the model with this number of frames per second
   * @param  {boolean} running=false - Initiate the model in a running state?
   * @param  {boolean} finished=false - Initiate the model in a finished state?
   */
  constructor(tick = 0, fps = 3, running = false, finished = false) {
    this.tick = tick;
    this.fps = fps;
    this.running = running;
    this.finished = running;
  }

  /** Start the model and keep it running until stopped */
  start() {
    this.running = true;
    this.step();
    startModelButton.firstElementChild.innerText = "Stop";
  }

  /** Stop the model */
  stop() {
    this.running = false;
    startModelButton.firstElementChild.innerText = "Start";
  }

  /**
   * Step the model one step ahead.
   *
   * If the model is in a running state this function will be called repeatedly
   * after the visualization elements are rendered. */
  step() {
    this.tick += 1;
    stepDisplay.innerText = this.tick;
    vizElements.update(this.tick);
  }

  /** Reset the model and visualization state but keep its running state */
  reset() {
    this.tick = 0;
    stepDisplay.innerText = this.tick;
    send({ type: "reset" });
    // Reset all the visualizations
    vizElements.reset();
    if (this.finished) {
      this.finished = false;
      startModelButton.firstElementChild.innerText = "Start";
    }
  }

  /** Stops the model and put it into a finished state */
  done() {
    this.stop();
    this.finished = true;
    startModelButton.firstElementChild.innerText = "Done";
  }

  /**
   * Update the frames per second
   * @param {number} val - The new value of frames per second
   */
  updateFPS(val) {
    this.fps = Number(val);
  }
}

export const controller = new ModelController();
// put controller in the global namespace of the browser
window.controller = controller;

const stepDisplay = document.getElementById("step");

const fpsControl = $("#fps").slider({
  max: 20,
  min: 0,
  value: 3,
  ticks: [0, 20],
  ticks_labels: [0, 20],
  ticks_position: [0, 100]
});
fpsControl.on("change", () => controller.updateFPS(fpsControl.val()));

/**
 * Button logic for start, stop and reset buttons
 */
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
