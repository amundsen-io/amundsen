// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import ClickableBadge from 'components/common/Badges';
import { getBadgeConfig } from 'config/config-utils';
import { Badge } from 'interfaces/Badges';

export interface BadgeListProps {
  badges: Badge[];
}

const BadgeList: React.FC<BadgeListProps> = ({ badges }: BadgeListProps) => {
  return (
    <span className="badge-list">
      {badges.map((badge, index) => {
        let badgeConfig;
        // search badges with just name
        if (badge.tag_name) {
          badgeConfig = getBadgeConfig(badge.tag_name);
        }
        // metadata badges with name and category
        else if (badge.badge_name) {
          badgeConfig = getBadgeConfig(badge.badge_name);
        }
        return (
          <ClickableBadge
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
