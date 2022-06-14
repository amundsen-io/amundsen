// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { v4 as uuidv4 } from 'uuid';

import { IconSizes } from 'interfaces';
import { IconProps } from './types';
import { DEFAULT_FILL_COLOR } from './constants';

export const RightTriangleIcon: React.FC<IconProps> = ({
  size = IconSizes.REGULAR,
  fill = DEFAULT_FILL_COLOR,
}: IconProps) => {
  const id = `right_triangle_${uuidv4()}`;

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <path
          d="M5.536 21.886C5.682 21.962 5.841 22 6 22C6.2 22 6.398 21.9401 6.569 21.8221L19.569 12.822C19.839 12.635 20 12.328 20 12C20 11.672 19.839 11.3651 19.569 11.1781L6.569 2.17805C6.264 1.96705 5.865 1.94205 5.536 2.11405C5.206 2.28705 5 2.62805 5 3.00005V21C5 21.372 5.206 21.713 5.536 21.886Z"
          id={id}
        />
      </defs>
      <g fill="none" fillRule="evenodd">
        <mask id="prefix__b" fill="#fff">
          <use xlinkHref={`#${id}`} />
        </mask>
        <use fill={fill} xlinkHref={`#${id}`} />
      </g>
    </svg>
  );
};
