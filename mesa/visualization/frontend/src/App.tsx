import React, { useState, useEffect, useCallback } from "react";
import { useWebSocket } from "./useWebsocket";
import { Sidebar } from "./components/Sidebar";
import { Aside, Divider, Group, Header, Slider } from "@mantine/core";
import { css } from "@emotion/css";
import { ControlButton } from "./components/ControlButton";

declare global {
  interface Window {
    control: {
      tick: number;
    };
    elements: { render: (vizState: unknown) => void }[];
    initElements: () => void;
  }
}

window.control = { tick: 0 };
window.elements = [];

export const App = () => {
  const model_name = "Model Name";
  const description = "Model Description";

  const [fps, setFps] = useState(3);
  const [running, setRunning] = useState(false);

  const { sendJSON, currentStep, done, vizState, modelParams } = useWebSocket();

  const requestNextStep = useCallback(() => {
    sendJSON({
      type: "get_step",
      data: { step: currentStep + 1 },
    });
  }, [currentStep, sendJSON]);

  useEffect(() => {
    window.initElements();
    sendJSON({ type: "reset" });

    // cleanup function only relevant for react development mode
    return () => {
      const elementsTopbar = document.getElementById("elements-topbar");
      const elements = document.getElementById("elements");

      if (elements && elementsTopbar) {
        elements.innerHTML = "";
        elements.appendChild(elementsTopbar);
        window.elements = [];
      }
      sendJSON({ type: "reset" });
    };
  }, []);

  useEffect(() => {
    window.control.tick = currentStep;
  }, [currentStep]);

  useEffect(() => {
    if (!vizState) {
      return;
    }
    window.elements.forEach((element, index) => {
      element.render(vizState[index]);
    });
  }, [vizState]);

  useEffect(() => {
    if (running && !done) {
      const timeout = setTimeout(() => {
        requestNextStep();
      }, 1000 / fps);

      return () => clearTimeout(timeout);
    }
  }, [running, done, currentStep, fps, requestNextStep]);

  const handleClickStartStop = () => {
    setRunning(!running);
  };

  const handleClickStep = () => {
    requestNextStep();
  };

  const handleClickReset = () => {
    setRunning(false);
    sendJSON({ type: "reset" });
  };

  return (
    <>
      <Header
        height={56}
        styles={(theme) => ({
          root: {
            backgroundColor: theme.colors.dark[6],
            display: "flex",
            flexDirection: "row",
          },
        })}
      >
        <h3 style={{ color: "grey" }}>{model_name}</h3>
        <Group position="right" style={{ flex: 1 }}>
          <ControlButton onClick={handleClickStartStop}>
            {running ? "Stop" : "Start"}
          </ControlButton>
          <ControlButton onClick={handleClickStep}>Step</ControlButton>
          <ControlButton onClick={handleClickReset}>Reset</ControlButton>
        </Group>
      </Header>
      <div
        className={css`
          display: flex;
          padding: 16px;
        `}
      >
        <Aside sx={{ flex: 1 }}>
          <Sidebar modelParams={modelParams} send={sendJSON} />
        </Aside>
        <Divider orientation="vertical" sx={{ height: "100vh" }} mx="md" />
        <div id="elements" style={{ flex: 2 }}>
          <div id="elements-topbar">
            <Slider
              defaultValue={fps}
              min={0}
              max={20}
              marks={[
                { value: 0, label: 0 },
                { value: 20, label: 20 },
              ]}
              label={(value) => value.toPrecision(1)}
              onChangeEnd={(value) => setFps(value)}
            />
            <p>Current Step: {currentStep}</p>
          </div>
        </div>
      </div>
    </>
  );
};
