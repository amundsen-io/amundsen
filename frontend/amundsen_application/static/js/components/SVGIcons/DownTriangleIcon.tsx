// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { v4 as uuidv4 } from 'uuid';

import { IconSizes } from 'interfaces';
import { IconProps } from './types';
import { DEFAULT_FILL_COLOR } from './constants';

export const DownTriangleIcon: React.FC<IconProps> = ({
  size = IconSizes.REGULAR,
  fill = DEFAULT_FILL_COLOR,
}: IconProps) => {
  const id = `down_triangle_${uuidv4()}`;

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <path
          d="M11.1783 19.569C11.3643 19.839 11.6723 20 12.0003 20C12.3283 20 12.6363 19.839 12.8223 19.569L21.8223 6.569C22.0343 6.263 22.0583 5.865 21.8853 5.536C21.7133 5.207 21.3723 5 21.0003 5H3.0003C2.6283 5 2.2873 5.207 2.1143 5.536C1.9413 5.865 1.9663 6.263 2.1783 6.569L11.1783 19.569Z"
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
