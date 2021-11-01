// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { v4 as uuidv4 } from 'uuid';

import { IconSizes } from 'interfaces';
import { IconProps } from './types';
import { DEFAULT_FILL_COLOR } from './constants';

export const NestingArrow: React.FC<IconProps> = ({
  size = IconSizes.REGULAR,
  fill = DEFAULT_FILL_COLOR,
}: IconProps) => {
  const id = `nesting_arrow_${uuidv4()}`;

  return (
    <svg
      className="nesting-arrow-icon"
      width={size}
      height={size}
      id={id}
      viewBox="0 0 20 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M1 12H0.5V12.5H1V12ZM13 12L8 9.11325V14.8868L13 12ZM0.5 0V12H1.5V0H0.5ZM1 12.5H8.5V11.5H1V12.5Z"
        fill={fill}
      />
    </svg>
  );
};
