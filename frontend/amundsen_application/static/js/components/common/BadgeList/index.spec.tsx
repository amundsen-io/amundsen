// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import ClickableBadge from 'components/common/Badges';
import { BadgeStyle } from 'config/config-types';
import * as ConfigUtils from 'config/config-utils';
import { Badge } from 'interfaces/Badges';
import BadgeList from '.';

describe('BadgeList', () => {
  const getBadgeConfigSpy = jest.spyOn(ConfigUtils, 'getBadgeConfig');
  getBadgeConfigSpy.mockImplementation((badgeName: string) => {
    return {
      displayName: badgeName + ' test name',
      style: BadgeStyle.PRIMARY,
    };
  });

  describe('BadgeList function component', () => {
    const badges: Badge[] = [
      {
        badge_name: 'beta',
        category: 'table_status',
      },
      {
        badge_name: 'Core Concepts',
        category: 'coco',
      },
    ];

    const badgeList = shallow(<BadgeList badges={badges} />);

    it('renders a badge-list element', () => {
      const container = badgeList.find('.badge-list');
      expect(container.exists()).toBe(true);
    });

    it('renders a <ClickableBadge> for each badge in the input', () => {
      expect(badgeList.find(ClickableBadge).length).toEqual(badges.length);
    });

    it('passes the correct props to the Clickable Badge', () => {
      badges.forEach((badge, index) => {
        const clickableBadge = badgeList.childAt(index);
        const clickableBadgeProps = clickableBadge.props();
        const badgeConfig = ConfigUtils.getBadgeConfig(badge.badge_name);
        expect(clickableBadgeProps.text).toEqual(badgeConfig.displayName);
        expect(clickableBadgeProps.labelStyle).toEqual(badgeConfig.style);
      });
    });
  });
});
