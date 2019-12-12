import * as React from 'react';
import { shallow } from 'enzyme';

import BadgeList from '../'
import Flag from 'components/common/Flag';
import { BadgeStyle } from 'config/config-types';
import * as ConfigUtils from 'config/config-utils';
import { Badge, TagType } from 'interfaces/Tags';

describe('BadgeList', () => {
  const getBadgeConfigSpy = jest.spyOn(ConfigUtils, 'getBadgeConfig');
  getBadgeConfigSpy.mockImplementation((badgeName: string) => {
    return {
      displayName: badgeName + " test name",
      style: BadgeStyle.PRIMARY,
    };
  });

  describe('BadgeList function component', () => {
    const badges: Badge[] = [
      {
        tag_name: 'test_1',
        tag_type: TagType.BADGE,
      },
      {
        tag_name: 'test_3',
        tag_type: TagType.BADGE,
      },
    ];

    const badgeList = shallow(<BadgeList badges={ badges } />);

    it('renders a badge-list element', () => {
      const container = badgeList.find('.badge-list')
      expect(container.exists()).toBe(true);
    });

    it('renders a <Flag> for each badge in the input', () => {
      expect(badgeList.find(Flag).length).toEqual(badges.length);
    });

    it('passes the correct props to the flag', () => {
      badges.forEach((badge, index) => {
        const flag = badgeList.childAt(index);
        const flagProps = flag.props();
        const badgeConfig = ConfigUtils.getBadgeConfig(badge.tag_name);
        expect(flagProps.text).toEqual(badgeConfig.displayName);
        expect(flagProps.labelStyle).toEqual(badgeConfig.style);
      });
    });
  });
});
