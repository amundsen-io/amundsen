// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { IconSizes, IconProps } from './types';

const DEFAULT_STROKE_COLOR = '';
const DEFAULT_FILL_COLOR = '#9191A8'; // gray40

export const RightIcon: React.FC<IconProps> = ({
  stroke = DEFAULT_STROKE_COLOR,
  size = IconSizes.REGULAR,
  fill = DEFAULT_FILL_COLOR,
}: IconProps) => {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24">
      <title>Right</title>
      <defs>
        <path
          d="M11.836 12.968l4.05-3.897a1.02 1.02 0 011.427.014.981.981 0 01-.014 1.4l-4.73 4.553c-.18.174-.409.268-.641.283a1.026 1.026 0 01-.806-.276l-4.83-4.566a.972.972 0 01-.019-1.394 1.028 1.028 0 011.434-.02l4.129 3.903z"
          id="prefix__a"
        />
      </defs>
      <g fill="none" fillRule="evenodd">
        <mask id="prefix__b" fill="#fff">
          <use xlinkHref="#prefix__a" />
        </mask>
        <use
          fill={fill}
          xlinkHref="#prefix__a"
          stroke={stroke}
          transform="rotate(-90 11.794 12.055)"
        />
      </g>
    </svg>
  );
};
