// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import ClickableBadge from 'components/common/Badges';
import { getBadgeConfig } from 'config/config-utils';
import { BadgeStyle } from 'config/config-types';
import { Badge } from 'interfaces/Tags';

export interface BadgeListProps {
  badges: any[]; // TODO replace with new badges later @allisonsuarez
}

/*
 * maps badge type to a badge style
 */
function mapBadgeStyle(badgeType: string): BadgeStyle {
  if (badgeType === 'negative') return BadgeStyle.DANGER;
  if (badgeType === 'positive') return BadgeStyle.SUCCESS;
  if (badgeType === 'warning') return BadgeStyle.WARNING;
  return BadgeStyle.DEFAULT;
}

const BadgeList: React.FC<BadgeListProps> = ({ badges }: BadgeListProps) => {
  return (
    <span className="badge-list">
      {badges.map((badge, index) => {
        if (badge.tag_name) {
          const badgeConfig = getBadgeConfig(badge.tag_name);
          return (
            <ClickableBadge
              text={badgeConfig.displayName}
              labelStyle={badgeConfig.style}
              key={`badge-${index}`}
            />
          );
        }
        if (badge.badge_name) {
          return (
            <ClickableBadge
              text={badge.badge_name}
              labelStyle={mapBadgeStyle(badge.badge_type)}
              key={`badge-${index}`}
            />
          );
        }
      })}
    </span>
  );
};

export default BadgeList;
