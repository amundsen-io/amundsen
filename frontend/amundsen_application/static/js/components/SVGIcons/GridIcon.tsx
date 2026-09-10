// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { IconSizes } from 'interfaces';
import { IconProps } from './types';

const DEFAULT_FILL_COLOR = 'currentColor';

export const GridIcon: React.FC<IconProps> = ({
  fill = DEFAULT_FILL_COLOR,
  size = IconSizes.REGULAR,
}: IconProps) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill={fill}
    className="grid-svg-icon"
  >
    <path d="M4 4h4v4H4zm6 0h4v4h-4zm6 0h4v4h-4zM4 10h4v4H4zm6 0h4v4h-4zm6 0h4v4h-4zM4 16h4v4H4zm6 0h4v4h-4zm6 0h4v4h-4z" />
  </svg>
);
