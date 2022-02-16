// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { v4 as uuidv4 } from 'uuid';

import { IconSizes } from 'interfaces';
import { IconProps } from './types';
import { DEFAULT_CIRCLE_FILL_COLOR } from './constants';

export const GraphIcon: React.FC<IconProps> = ({
  size = IconSizes.REGULAR,
  fill = DEFAULT_CIRCLE_FILL_COLOR,
}: IconProps) => {
  const id = `graph_icon_${uuidv4()}`;

  return (
    <svg viewBox="0 0 25 25" height={size} width={size}>
      <defs>
        <path
          d="M12,0.259C5.516,0.259,0.258,5.516,0.258,12c0,6.486,5.258,11.74,11.742,11.74S23.742,18.486,23.742,12
            C23.742,5.516,18.484,0.259,12,0.259z M18.896,10.467c-0.137,0-0.268,0-0.383-0.054l-2.735,2.736
            c0.053,0.115,0.053,0.244,0.053,0.383c0,0.846-0.684,1.533-1.531,1.533s-1.531-0.688-1.531-1.533l0.053-0.383l-1.97-1.97
            c-0.245,0.054-0.521,0.054-0.766,0l-3.501,3.501l0.054,0.385c0,0.846-0.686,1.531-1.533,1.531s-1.533-0.686-1.533-1.531
            c0-0.848,0.686-1.533,1.533-1.533l0.383,0.055l3.502-3.503C8.851,9.586,8.981,9.019,9.387,8.62c0.598-0.605,1.564-0.605,2.161,0
            c0.407,0.398,0.536,0.966,0.398,1.463l1.97,1.969l0.383-0.054c0.137,0,0.268,0,0.383,0.054l2.734-2.735
            c-0.053-0.115-0.053-0.245-0.053-0.383c0-0.847,0.688-1.532,1.532-1.532c0.848,0,1.532,0.686,1.532,1.532
            S19.743,10.467,18.896,10.467z"
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
