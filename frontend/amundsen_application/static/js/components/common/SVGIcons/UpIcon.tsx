// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { IconSizes, IconProps } from './types';

const DEFAULT_STROKE_COLOR = '';
const DEFAULT_FILL_COLOR = '#D6D9DB';

export const UpIcon: React.FC<IconProps> = ({
  stroke = DEFAULT_STROKE_COLOR,
  size = IconSizes.REGULAR,
  fill = DEFAULT_FILL_COLOR,
}: IconProps) => {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24">
      <title>Up</title>
      <defs>
        <path
          d="M12.097 12.12l4.049-3.898a1.02 1.02 0 011.427.014.981.981 0 01-.013 1.4l-4.73 4.553c-.18.174-.41.268-.642.283a1.026 1.026 0 01-.805-.276L6.553 9.63a.972.972 0 01-.02-1.394 1.028 1.028 0 011.434-.02l4.13 3.904z"
          id="prefix__a"
        />
      </defs>
      <g fill="none" fillRule="evenodd">
        <mask id="prefix__b" fill="#fff">
          <use xlinkHref="#prefix__a" />
        </mask>
        <use
          fill={fill}
          stroke={stroke}
          transform="rotate(-180 12.055 11.206)"
          xlinkHref="#prefix__a"
        />
      </g>
    </svg>
  );
};
