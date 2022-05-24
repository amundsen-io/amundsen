// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { IconProps } from './types';
import {
  DEFAULT_CIRCLE_FILL_COLOR,
  DEFAULT_CIRCLE_ICON_FILL_COLOR,
} from './constants';

export const CodeIcon: React.FC<IconProps> = ({
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
      d="M6.91671 13.1873L7.75004 12.146L5.06737 9.99996L7.75004 7.85396L6.91671 6.81262L3.58337 9.47929C3.42537 9.60595 3.33337 9.79729 3.33337 9.99996C3.33337 10.2026 3.42537 10.394 3.58337 10.5206L6.91671 13.1873ZM13.0834 6.81262L12.25 7.85396L14.9327 9.99996L12.25 12.146L13.0834 13.1873L16.4167 10.5206C16.5747 10.394 16.6667 10.2026 16.6667 9.99996C16.6667 9.79729 16.5747 9.60595 16.4167 9.47929L13.0834 6.81262Z"
      fill={DEFAULT_CIRCLE_ICON_FILL_COLOR}
    />
    <path
      d="M11.984 4.14429L9.31773 16.1443L8.01549 15.855L10.6818 3.85494L11.984 4.14429Z"
      fill={DEFAULT_CIRCLE_ICON_FILL_COLOR}
    />
  </svg>
);
