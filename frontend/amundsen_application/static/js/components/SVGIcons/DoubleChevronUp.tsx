// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { v4 as uuidv4 } from 'uuid';

import { IconSizes } from 'interfaces';
import { IconProps } from './types';
import { DEFAULT_FILL_COLOR } from './constants';

export const DoubleChevronUp: React.FC<IconProps> = ({
  size = IconSizes.REGULAR,
  fill = DEFAULT_FILL_COLOR,
}: IconProps) => {
  const id = `double_chevron_up_${uuidv4()}`;

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
        d="M6.29297 11.293L7.70697 12.707L12 8.414L16.293 12.707L17.707 11.293L12 5.586L6.29297 11.293Z"
        fill={fill}
      />
      <path
        d="M6.29297 16.293L7.70697 17.707L12 13.414L16.293 17.707L17.707 16.293L12 10.586L6.29297 16.293Z"
        fill={fill}
      />
    </svg>
  );
};
