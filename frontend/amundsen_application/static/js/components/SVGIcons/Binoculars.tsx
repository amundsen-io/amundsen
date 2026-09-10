// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { IconSizes } from 'interfaces';
import { IconProps } from './types';
import { DEFAULT_FILL_COLOR } from './constants';

export const Binoculars: React.FC<IconProps> = ({
  size = IconSizes.REGULAR,
  fill = DEFAULT_FILL_COLOR,
}: IconProps) => (
  <svg
    viewBox="0 0 24 24"
    width={size}
    height={size}
    fill={fill}
    className="binoculars-svg-icon"
  >
    <path d="M19.447 5.345A3.27 3.27 0 0016.29 3a3.293 3.293 0 00-3.277 3h-2.025a3.297 3.297 0 00-3.284-3 3.268 3.268 0 00-3.151 2.345l-2.511 8.368A1.027 1.027 0 002 14v1a5.006 5.006 0 005.001 5 5.003 5.003 0 004.576-3h.846a5.003 5.003 0 004.576 3A5.006 5.006 0 0022 14.999V14c0-.098-.015-.194-.042-.287l-2.511-8.368zM7.001 18A3.005 3.005 0 014 15c0-.076.017-.147.022-.222A2.995 2.995 0 017 12a3 3 0 013 3v.009A3.004 3.004 0 017.001 18zm9.998 0A3.004 3.004 0 0114 15.009V15a3 3 0 016-.001A3.005 3.005 0 0116.999 18z" />
  </svg>
);
