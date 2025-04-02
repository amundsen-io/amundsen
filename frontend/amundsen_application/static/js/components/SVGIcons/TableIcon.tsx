// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { IconProps } from './types';
import {
  DEFAULT_CIRCLE_FILL_COLOR,
  DEFAULT_CIRCLE_ICON_FILL_COLOR,
} from './constants';

export const TableIcon: React.FC<IconProps> = ({
  fill = DEFAULT_CIRCLE_FILL_COLOR,
}: IconProps) => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 20 20"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="50%" cy="50%" r="50%" fill={fill} />
    <path
      d="M15.262 4.00067H4.66667C3.93133 4.00067 3.33333 4.59867 3.33333 5.334V14.6673C3.33333 15.4027 3.93133 16.0007 4.66667 16.0007H15.262C15.9973 16.0007 16.5953 15.4027 16.5953 14.6673V7.33333V6.66667V6V5.334V5.33333C16.5947 4.598 15.996 4.00067 15.262 4.00067ZM7.33333 14.6673H4.66667V7.33333H7.33333V14.6673ZM11.3333 14.6673H8.66667V7.33333H11.3333V14.6673ZM12.6667 14.6673V7.33333H15.262L15.2627 14.6673H12.6667V14.6673Z"
      fill={DEFAULT_CIRCLE_ICON_FILL_COLOR}
    />
  </svg>
);
