// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { IconSizes, IconProps } from './types';

const DEFAULT_STROKE_COLOR = '';
const DEFAULT_FILL_COLOR = '#D6D9DB';

export const DownIcon: React.FC<IconProps> = ({
  stroke = DEFAULT_STROKE_COLOR,
  size = IconSizes.REGULAR,
  fill = DEFAULT_FILL_COLOR,
}: IconProps) => {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24">
      <title>Down</title>
      <defs>
        <path
          d="M11.987 13.73l4.051-3.918a1.017 1.017 0 011.426.012.983.983 0 01-.012 1.403l-4.733 4.578a1.013 1.013 0 01-.63.283 1.024 1.024 0 01-.814-.277l-4.833-4.59a.975.975 0 01-.018-1.397 1.026 1.026 0 011.432-.018l4.131 3.924z"
          id="prefix__a"
        />
      </defs>
      <g fill="none" fillRule="evenodd">
        <mask id="prefix__b" fill="#fff">
          <use xlinkHref="#prefix__a" />
        </mask>
        <use fill={fill} xlinkHref="#prefix__a" stroke={stroke} />
      </g>
    </svg>
  );
};
