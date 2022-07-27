import { useRef, useEffect, useState } from "react";
import { WSIncomingMessage, WSOutgoingMessage } from "./types.ts/WSMessage";

const url = `${
  (window.location.protocol === "https:" ? "wss://" : "ws://") + location.host
}/ws`;

const socket = new WebSocket(url);

export const useWebSocket = () => {
  const [vizState, setVizState] = useState([]);
  const [done, setDone] = useState(false);
  const [modelParams, setModelParams] = useState({});
  const [currentStep, setCurrentStep] = useState(0);

  const ws = useRef<WebSocket>(socket);

  const sendJSON = (msg: WSOutgoingMessage) => {
    console.log("Sending:", msg);
    ws.current.send(JSON.stringify(msg));
  };

  useEffect(() => {
    ws.current.onopen = () => sendJSON({ type: "reset" });
    ws.current.onclose = () => console.log("ws closed");
    ws.current.onmessage = (message: WSIncomingMessage) => {
      const msg = JSON.parse(message.data);
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
