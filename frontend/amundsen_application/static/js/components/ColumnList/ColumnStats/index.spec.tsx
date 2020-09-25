// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { mount } from 'enzyme';

import ColumnStats, { ColumnStatsProps } from '.';
import TestDataBuilder from './testDataBuilder';

const dataBuilder = new TestDataBuilder();

const setup = (propOverrides?: Partial<ColumnStatsProps>) => {
  const props = {
    stats: [],
    ...propOverrides,
  };
  const wrapper = mount<typeof ColumnStats>(<ColumnStats {...props} />);

  return { props, wrapper };
};

describe('ColumnStats', () => {
  describe('render', () => {
    describe('when stats are empty', () => {
      const { stats } = dataBuilder.withEmptyStats().build();

      it('does not render the component', () => {
        const { wrapper } = setup({ stats });
        const expected = stats.length;
        const actual = wrapper.find('.column-stats').length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when four stats are passed', () => {
      const { stats } = dataBuilder.withFourStats().build();

      it('renders the component', () => {
        const { wrapper } = setup({ stats });
        const expected = 1;
        const actual = wrapper.find('.column-stats').length;

        expect(actual).toEqual(expected);
      });

      it('renders two columns', () => {
        const { wrapper } = setup({ stats });
        const expected = 2;
        const actual = wrapper.find('.column-stats-column').length;

        expect(actual).toEqual(expected);
      });

      it('renders the stats info text', () => {
        const { wrapper } = setup({ stats });
        const expected = 1;
        const actual = wrapper.find('.stat-collection-info').length;

        expect(actual).toEqual(expected);
      });

      it('renders four stat rows', () => {
        const { wrapper } = setup({ stats });
        const expected = stats.length;
        const actual = wrapper.find('.column-stat-row').length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when three stats are passed', () => {
      const { stats } = dataBuilder.withThreeStats().build();

      it('renders three stat rows', () => {
        const { wrapper } = setup({ stats });
        const expected = stats.length;
        const actual = wrapper.find('.column-stat-row').length;

        expect(actual).toEqual(expected);
      });

      it('renders two rows in the first column', () => {
        const { wrapper } = setup({ stats });
        const expected = 2;
        const actual = wrapper
          .find('.column-stats-column')
          .first()
          .find('.column-stat-row').length;

        expect(actual).toEqual(expected);
      });

      it('renders one row in the second column', () => {
        const { wrapper } = setup({ stats });
        const expected = 1;
        const actual = wrapper
          .find('.column-stats-column')
          .last()
          .find('.column-stat-row').length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when eight stats are passed', () => {
      const { stats } = dataBuilder.withEightStats().build();

      it('renders eight stat rows', () => {
        const { wrapper } = setup({ stats });
        const expected = stats.length;
        const actual = wrapper.find('.column-stat-row').length;

        expect(actual).toEqual(expected);
      });
    });
  });
});
