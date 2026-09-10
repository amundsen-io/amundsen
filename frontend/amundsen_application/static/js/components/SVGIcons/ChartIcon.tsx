// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { IconProps } from './types';
import {
  DEFAULT_CIRCLE_FILL_COLOR,
  DEFAULT_CIRCLE_ICON_FILL_COLOR,
} from './constants';

export const ChartIcon: React.FC<IconProps> = ({
  fill = DEFAULT_CIRCLE_FILL_COLOR,
}: IconProps) => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 20 20"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M20 10C20 15.5228 15.5228 20 10 20C4.47715 20 0 15.5228 0 10C0 4.47715 4.47715 0 10 0C15.5228 0 20 4.47715 20 10Z"
      fill={fill}
    />
    <path
      d="M4 4V15.3333C4 15.702 4.298 16 4.66667 16H16V14.6667H5.33333V4H4Z"
      fill={DEFAULT_CIRCLE_ICON_FILL_COLOR}
    />
    <path
      d="M12.1954 11.8047C12.4561 12.0654 12.8774 12.0654 13.1381 11.8047L16.4714 8.47135L15.5287 7.52869L12.6667 10.3907L11.1381 8.86202C10.8774 8.60135 10.4561 8.60135 10.1954 8.86202L6.86206 12.1954L7.80473 13.138L10.6667 10.276L12.1954 11.8047Z"
      fill={DEFAULT_CIRCLE_ICON_FILL_COLOR}
    />
  </svg>
);
