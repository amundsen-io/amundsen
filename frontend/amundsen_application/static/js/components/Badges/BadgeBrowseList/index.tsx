// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Badge } from 'interfaces/Badges';
import BadgeList from 'features/BadgeList';
import './styles.scss';
import {
  AVAILABLE_BADGES_TITLE,
  BROWSE_BADGES_TITLE,
} from 'components/Badges/BadgeBrowseList/constants';
import { isShowBadgesInHomeEnabled } from 'config/config-utils';

export interface BadgeBrowseListProps {
  badges: Badge[];
  shortBadgesList?: boolean;
}

const BadgeBrowseListShort: React.FC<BadgeBrowseListProps> = ({
  badges,
}: BadgeBrowseListProps) => {
  const hasBadges = badges.length > 0;
  if (hasBadges && isShowBadgesInHomeEnabled()) {
    return (
      <article className="badges-browse-section badges-browse-section-short">
        <h2 className="available-badges-header-title">
          {AVAILABLE_BADGES_TITLE}
        </h2>
        <BadgeList badges={badges} />
      </article>
    );
  }
  // do not show component at all if there are no badges to be shown
  return null;
};

const BadgeBrowseListLong: React.FC<BadgeBrowseListProps> = ({
  badges,
}: BadgeBrowseListProps) => (
  <article className="badges-browse-section badges-browse-section-long">
    <h1 className="header-title">{BROWSE_BADGES_TITLE}</h1>
    <hr className="header-hr" />
    <label className="section-label">
      <span className="section-title title-2">{AVAILABLE_BADGES_TITLE}</span>
    </label>
    <BadgeList badges={badges} />
  </article>
);

const BadgeBrowseList: React.FC<BadgeBrowseListProps> = ({
  badges,
  shortBadgesList,
}: BadgeBrowseListProps) => {
  if (shortBadgesList) {
    return <BadgeBrowseListShort badges={badges} />;
  }

  return <BadgeBrowseListLong badges={badges} />;
};

export default BadgeBrowseList;
