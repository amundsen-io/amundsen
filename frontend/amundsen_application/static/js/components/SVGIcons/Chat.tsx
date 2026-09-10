// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { IconSizes } from 'interfaces';
import { IconProps } from './types';
import { DEFAULT_FILL_COLOR } from './constants';

export const Chat: React.FC<IconProps> = ({
  size = IconSizes.REGULAR,
  fill = DEFAULT_FILL_COLOR,
}: IconProps) => (
  <svg viewBox="0 0 24 24" width={size} height={size} fill={fill}>
    <path d="M4 18h2v4.081L11.101 18H16c1.103 0 2-.897 2-2V8c0-1.103-.897-2-2-2H4c-1.103 0-2 .897-2 2v8c0 1.103.897 2 2 2z" />
    <path d="M20 2H8c-1.103 0-2 .897-2 2h12c1.103 0 2 .897 2 2v8c1.103 0 2-.897 2-2V4c0-1.103-.897-2-2-2z" />
  </svg>
);
