import * as React from 'react';

import { IconSizes } from '.';

const DEFAULT_STROKE_COLOR = 'currentColor';

export interface IconProps {
  stroke?: string;
  size?: number;
}

export const AlertIcon: React.FC<IconProps> = ({
  stroke = DEFAULT_STROKE_COLOR,
  size = IconSizes.REGULAR,
}: IconProps) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={stroke}
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className="alert-triangle-svg-icon"
    >
      <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0zM12 9v4M12 17h0" />
    </svg>
  );
};
