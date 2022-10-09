import { Badge, Stack } from "@mantine/core";
import { WSOutgoingMessage } from "../types";
import { UserInput, UserSettableParameter } from "./UserSettableParameter";

type SidebarProps = {
  modelParams: { [name: string]: UserInput };
  send: (msg: WSOutgoingMessage) => void;
};

export const Sidebar = ({ modelParams = {}, send }: SidebarProps) => {
  const handleChange = (param_name: string) => {
    return (value: unknown) =>
      send({ type: "submit_params", param: param_name, value: value });
  };

  return (
    <Stack spacing="lg" align="unset">
      {Object.entries(modelParams).map(([name, param]) => {
        return (
          <div key={name}>
            <Badge sx={{ alignSelf: "flex-start" }}>{param.name}</Badge>
            <UserSettableParameter
              param={param}
              onChange={handleChange(name)}
            />
          </div>
        );
      })}
    </Stack>
  );
};
