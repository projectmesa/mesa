import { UserInput } from "./components/UserSettableParameter";

export type WSIncomingMessage =
  | VizStateMessage
  | EndMessage
  | ModelParamsMessage;

export type WSOutgoingMessage =
  | GetStepMessage
  | ResetMessage
  | SubmitParamsMessage;

type VizStateMessage = {
  type: "viz_state";
  data: unknown[];
  step: number;
};

type EndMessage = {
  type: "end";
};

type ModelParamsMessage = {
  type: "model_params";
  params: { [name: string]: UserInput };
};

type GetStepMessage = {
  type: "get_step";
  data: { step: number };
};

type ResetMessage = {
  type: "reset";
};

type SubmitParamsMessage = {
  type: "submit_params";
  param: string;
  value: unknown;
};
