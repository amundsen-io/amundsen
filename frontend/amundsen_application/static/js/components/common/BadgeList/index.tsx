// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import Flag from 'components/common/Flag';
import { getBadgeConfig } from 'config/config-utils';
import { Badge } from 'interfaces/Tags';

export interface BadgeListProps {
  badges: Badge[];
}

const BadgeList: React.SFC<BadgeListProps> = ({ badges }: BadgeListProps) => {
  return (
    <span className="badge-list">
      {badges.map((badge, index) => {
        const badgeConfig = getBadgeConfig(badge.tag_name);

        return (
          <Flag
            text={badgeConfig.displayName}
            labelStyle={badgeConfig.style}
            key={`badge-${index}`}
          />
        );
      })}
    </span>
  );
};

export default BadgeList;
