export type WSIncomingMessage = {
  type: string;
  data: unknown;
};

export type WSOutgoingMessage = {
  type: "get_step";
};
