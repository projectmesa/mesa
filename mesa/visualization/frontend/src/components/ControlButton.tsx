import { Button, ButtonProps } from "@mantine/core";
import React from "react";

export const ControlButton = ({ children, onClick }: ButtonProps<"button">) => (
  <Button compact size="md" variant="subtle" onClick={onClick}>
    {children}
  </Button>
);
