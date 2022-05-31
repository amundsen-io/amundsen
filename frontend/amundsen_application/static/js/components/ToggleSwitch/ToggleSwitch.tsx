// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import Switch from 'react-switch';

export interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: any) => void;
}

const TOGGLE_ON_COLOR = '#665AFF';
const TOGGLE_HEIGHT = 20;
const TOGGLE_WIDTH = 38;

export const ToggleSwitch: React.FC<ToggleSwitchProps> = ({
  checked,
  onChange,
}: ToggleSwitchProps) => (
  <Switch
    checked={checked}
    onChange={onChange}
    checkedIcon={false}
    uncheckedIcon={false}
    className="toggle-switch"
    height={TOGGLE_HEIGHT}
    width={TOGGLE_WIDTH}
    onColor={TOGGLE_ON_COLOR}
  />
);

export default ToggleSwitch;
