// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import { BadgeStyle } from 'config/config-types';
import * as ConfigUtils from 'config/config-utils';
import { Badge } from 'interfaces/Badges';

import * as Analytics from 'utils/analytics';

import BadgeBrowseList, { BadgeBrowseListProps } from '.';

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

const setup = (propOverrides?: Partial<BadgeBrowseListProps>) => {
  const props = {
    badges,
    ...propOverrides,
  };
  const wrapper = shallow<typeof BadgeBrowseList>(
    <BadgeBrowseList {...props} />
  ).dive();
  return { props, wrapper };
};

const logClickSpy = jest.spyOn(Analytics, 'logClick');
logClickSpy.mockImplementation(() => null);

describe('BadgeBrowseList', () => {
  const getBadgeConfigSpy = jest.spyOn(ConfigUtils, 'getBadgeConfig');
  getBadgeConfigSpy.mockImplementation((badgeName: string) => ({
    displayName: badgeName + ' test name',
    style: BadgeStyle.PRIMARY,
  }));

  describe('render', () => {
    describe('when BadgeBrowseList called with shortBadgesList={false}', () => {
      it('renders component with browse header', () => {
        const { wrapper } = setup({ shortBadgesList: false });
        const expected = 1;
        const actualHeaders = wrapper.find('.header-title').length;
        const actualHrs = wrapper.find('.header-hr').length;

        expect(actualHeaders).toEqual(expected);
        expect(actualHrs).toEqual(expected);
      });
    });

    describe('when BadgeBrowseList called with shortBadgesList={true}', () => {
      it('renders component without browse header', () => {
        const { wrapper } = setup({ shortBadgesList: true });
        const expected = 0;
        const actualHeaders = wrapper.find('.header-title').length;
        const actualHrs = wrapper.find('.header-hr').length;

        expect(actualHeaders).toEqual(expected);
        expect(actualHrs).toEqual(expected);
      });
    });
  });
});
