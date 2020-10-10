// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Provider } from 'react-redux';
import { mount } from 'enzyme';
import configureStore from 'redux-mock-store';

import globalState from 'fixtures/globalState';
import Flag from 'components/common/Flag';
import { BadgeStyle } from 'config/config-types';
import * as ConfigUtils from 'config/config-utils';
import { Badge } from 'interfaces/Badges';
import BadgeList, { BadgeListProps } from '.';

const columnBadges: Badge[] = [
  {
    badge_name: 'col badge 1',
    category: 'column',
  },
  {
    badge_name: 'col badge 2',
    category: 'column',
  },
];
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

const middlewares = [];
const mockStore = configureStore(middlewares);

const setup = (propOverrides?: Partial<BadgeListProps>) => {
  const props = {
    badges: [],
    ...propOverrides,
  };

  const testState = globalState;
  testState.tableMetadata.tableData.badges = badges;
  const wrapper = mount<BadgeListProps>(
    <Provider store={mockStore(testState)}>
      <BadgeList {...props} />
    </Provider>
  );

  return { props, wrapper };
};

describe('BadgeList', () => {
  const getBadgeConfigSpy = jest.spyOn(ConfigUtils, 'getBadgeConfig');
  getBadgeConfigSpy.mockImplementation((badgeName: string) => {
    return {
      displayName: badgeName + ' test name',
      style: BadgeStyle.PRIMARY,
    };
  });

  describe('when no badges are passed', () => {
    it('renders a badge-list element', () => {
      const { wrapper } = setup();
      const expected = 1;
      const actual = wrapper.find('.badge-list').length;

      expect(actual).toEqual(expected);
    });

    it('does not render any badges', () => {
      const { wrapper } = setup();
      const actual = wrapper.find(Flag).length;
      const expected = 0;

      expect(actual).toEqual(expected);
    });
  });

  describe('when badges are passed', () => {
    it('renders a badge-list element', () => {
      const { wrapper } = setup({ badges });
      const expected = 1;
      const actual = wrapper.find('.badge-list').length;

      expect(actual).toEqual(expected);
    });

    it('renders a .actionable-badge for each badge in the input', () => {
      const { wrapper } = setup({ badges });
      const expected = badges.length;
      const actual = wrapper.find('.actionable-badge').length;

      expect(actual).toEqual(expected);
    });
  });

  describe('when badge category is column', () => {
    it('renders a badge-list element', () => {
      const { wrapper } = setup({ badges: columnBadges });
      const expected = 1;
      const actual = wrapper.find('.badge-list').length;

      expect(actual).toEqual(expected);
    });

    it('renders a .static-badge for each badge in the input', () => {
      const { wrapper } = setup({ badges: columnBadges });
      const expected = 2;
      const actual = wrapper.find('.static-badge').length;

      expect(actual).toEqual(expected);
    });
  });
});
