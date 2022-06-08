// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { v4 as uuidv4 } from 'uuid';

import { IconSizes } from 'interfaces';
import { IconProps } from './types';
import { DEFAULT_FILL_COLOR } from './constants';

export const DoubleChevronDown: React.FC<IconProps> = ({
  size = IconSizes.REGULAR,
  fill = DEFAULT_FILL_COLOR,
}: IconProps) => {
  const id = `double_chevron_down_${uuidv4()}`;

  return (
    <svg
      width={size}
      height={size}
      id={id}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 15.586L7.70697 11.293L6.29297 12.707L12 18.414L17.707 12.707L16.293 11.293L12 15.586Z"
        fill={fill}
      />
      <path
        d="M17.707 7.707L16.293 6.293L12 10.586L7.70697 6.293L6.29297 7.707L12 13.414L17.707 7.707Z"
        fill={fill}
      />
    </svg>
  );
};
