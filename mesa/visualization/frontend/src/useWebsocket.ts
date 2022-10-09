import { useRef, useEffect, useState } from "react";
import { UserInput } from "./components/UserSettableParameter";
import { WSIncomingMessage, WSOutgoingMessage } from "./types";

const url = `${
  (window.location.protocol === "https:" ? "wss://" : "ws://") + location.host
}/ws`;

const socket = new WebSocket(url);

export const useWebSocket = () => {
  const [vizState, setVizState] = useState<unknown[] | null>(null);
  const [done, setDone] = useState(false);
  const [modelParams, setModelParams] = useState<{
    [name: string]: UserInput;
  }>({});
  const [currentStep, setCurrentStep] = useState(0);

  const ws = useRef<WebSocket>(socket);

  const sendJSON = (msg: WSOutgoingMessage) => {
    console.log("Sending:", msg);
    ws.current.send(JSON.stringify(msg));
  };

  useEffect(() => {
    ws.current.onopen = () => sendJSON({ type: "reset" });
    ws.current.onclose = () => console.log("ws closed");
    ws.current.onmessage = (message: { data: string }) => {
      console.log(message);
      const msg: WSIncomingMessage = JSON.parse(message.data);
      console.log(msg);
      switch (msg["type"]) {
        case "viz_state":
          // Update visualization state
          setVizState(msg.data);
          setCurrentStep(msg.step);
          break;
        case "end":
          // We have reached the end of the model
          setDone(true);
          break;
        case "model_params":
          // Create GUI elements for each model parameter and reset everything
          setModelParams(msg.params);
          break;

        default:
          // There shouldn't be any other message
          console.log("Unexpected message.");
          console.log(msg);
      }

      return () => {
        ws.current.close();
      };
    };
  }, []);

  return {
    socket: ws.current,
    sendJSON,
    done,
    vizState,
    modelParams,
    currentStep,
  };
};
