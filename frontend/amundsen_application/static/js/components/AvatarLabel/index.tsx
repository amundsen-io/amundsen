// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as Avatar from 'react-avatar';

import './styles.scss';

export interface AvatarLabelProps {
  avatarClass?: string;
  labelClass?: string;
  label?: string;
  round?: boolean;
  src?: string;
}

const AvatarLabel: React.FC<AvatarLabelProps> = ({
  avatarClass,
  labelClass = 'text-secondary',
  label = '',
  round = true,
  src = '',
}: AvatarLabelProps) => (
  <div className="avatar-label-component">
    <Avatar
      className={avatarClass}
      name={label}
      src={src}
      size={24}
      round={round}
    />
    <span className={`avatar-label text-body-w2 ${labelClass}`}>{label}</span>
  </div>
);

export default AvatarLabel;
