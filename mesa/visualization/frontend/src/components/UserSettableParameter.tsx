import React from "react";
import { Checkbox, Slider } from "@mantine/core";

type SliderInput = {
  param_type: "slider";
  name: string;
  min_value: number;
  max_value: number;
  description?: string;
  value: number;
  step?: number;
};

type CheckboxInput = {
  param_type: "checkbox";
  name: string;
  description?: string;
  value: boolean;
};

export type UserInput = SliderInput | CheckboxInput;

type IProps = {
  param: UserInput;
  onChange: (value: any) => void;
};

export const UserSettableParameter = ({ param, onChange }: IProps) => {
  switch (param.param_type) {
    case "slider":
      return (
        <Slider
          key={param.name}
          defaultValue={param.value}
          min={param.min_value}
          max={param.max_value}
          marks={[
            { value: param.min_value, label: param.min_value },
            { value: param.max_value, label: param.max_value },
          ]}
          step={param.step}
          label={(value) => value.toPrecision(1)}
          onChangeEnd={(value) => onChange(value)}
        />
      );
    case "checkbox":
      return (
        <Checkbox
          key={param.name}
          label={param.name}
          defaultChecked={param.value}
          onChange={(e) => onChange(e.target.checked)}
        />
      );
  }
};
