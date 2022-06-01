import React, { useState, useEffect } from "react";
import { useWebSocket } from "./useWebsocket";
import Slider from "bootstrap-slider";
import "bootstrap-slider/dist/css/bootstrap-slider.min.css";
import { Sidebar } from "./Sidebar";

export const App = () => {
  const model_name = "Model Name";
  const description = "Model Description";

  const [fps, setFps] = useState(3);
  const [running, setRunning] = useState(false);

  const { sendJSON, currentStep, done, vizState, modelParams } = useWebSocket();

  useEffect(() => {
    window.control = { tick: 0 };
    window.elements = [];
    window.initElements();
    const fpsControl = new Slider(document.querySelector("#fps"), {
      max: 20,
      min: 0,
      value: fps,
      ticks: [0, 20],
      ticks_labels: [0, 20],
      ticks_position: [0, 100],
    });

    fpsControl.on("change", () => setFps(fpsControl.getValue()));

    // cleanup function only relevant for react development mode
    return () => {
      const elementsTopbar = document.getElementById("elements-topbar");
      const elements = document.getElementById("elements");

      if (elements) {
        elements.innerHTML = "";
        elements.appendChild(elementsTopbar);
        window.elements = [];
      }
    };
  }, []);

  useEffect(() => {
    window.control.tick = currentStep;
  }, [currentStep]);

  useEffect(() => {
    if (!vizState) return;
    window.elements.forEach((element, index) => {
      element.render(vizState[index]);
    });
  }, [vizState]);

  useEffect(() => {
    if (running && !done) {
      const timeout = setTimeout(() => {
        sendJSON({
          type: "get_step",
          data: { step: currentStep },
        });
      }, 1000 / fps);

      return () => clearTimeout(timeout);
    }
  }, [running, done, currentStep, fps]);

  const handleClickStartStop = () => {
    setRunning(!running);
  };

  const handleClickStep = () => {
    sendJSON({ type: "get_step", data: { step: currentStep } });
  };

  const handleClickReset = () => {
    setRunning(false);
    sendJSON({ type: "reset" });
  };

  return (
    // Navbar
    <>
      <nav className="navbar navbar-dark bg-dark navbar-static-top navbar-expand-md mb-3">
        <div className="container">
          <button
            type="button"
            className="navbar-toggler collapsed"
            data-toggle="collapse"
            data-target="#navbar"
            aria-expanded="false"
            aria-controls="navbar"
          >
            <span className="sr-only">Toggle navigation</span>
            &#x2630;
          </button>
          <a className="navbar-brand" href="#">
            {model_name}
          </a>
          <div id="navbar" className="navbar-collapse collapse">
            <ul className="nav navbar-nav">
              <li className="nav-item">
                <a
                  href="#"
                  data-toggle="modal"
                  data-target="#about"
                  data-title="About"
                  data-content="#about-content"
                  className="nav-link"
                >
                  About
                </a>
              </li>
            </ul>
            <ul className="nav navbar-nav ml-auto">
              <li id="play-pause" className="nav-item">
                <a href="#" className="nav-link" onClick={handleClickStartStop}>
                  {running ? "Stop" : "Start"}
                </a>
              </li>
              <li id="step" className="nav-item">
                <a href="#" className="nav-link" onClick={handleClickStep}>
                  Step
                </a>
              </li>
              <li id="reset" className="nav-item">
                <a href="#" className="nav-link" onClick={handleClickReset}>
                  Reset
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      <div className="container d-flex flex-row">
        <Sidebar modelParams={modelParams} send={sendJSON} />
        <div className="col-xl-8 col-lg-8 col-md-8 col-9" id="elements">
          <div id="elements-topbar">
            <div>
              <label
                className="badge badge-primary"
                htmlFor="fps"
                style={{ marginRight: 15 }}
              >
                Frames Per Second
              </label>
              <input id="fps" data-slider-id="fps" type="text" />
            </div>
            <p>
              Current Step: <span id="currentStep">{currentStep}</span>
            </p>
          </div>
        </div>
      </div>
      <div id="about" className="modal fade" tabIndex={-1} role="dialog">
        <div className="modal-dialog modal-lg">
          <div className="modal-content">
            <div className="modal-header">
              <h4 className="modal-title">About {model_name}</h4>
              <button
                type="button"
                className="close"
                data-dismiss="modal"
                aria-label="Close"
              >
                <span aria-hidden="true">&#xD7;</span>
              </button>
            </div>
            <div className="modal-body">
              <div>{description}</div>
              <div>&#xA0;</div>
              <div style={{ clear: "both" }}></div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
