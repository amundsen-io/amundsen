// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';
import { ColumnStats, ColumnStatsProps } from '.';

describe('ColumnStats', () => {
  const setup = (propOverrides?: Partial<ColumnStatsProps>) => {
    const props = {
      stats: [
        {
          end_epoch: 1571616000,
          start_epoch: 1571616000,
          stat_type: 'count',
          stat_val: '12345',
        },
        {
          end_epoch: 1571616000,
          start_epoch: 1571616000,
          stat_type: 'count_null',
          stat_val: '123',
        },
        {
          end_epoch: 1571616000,
          start_epoch: 1571616000,
          stat_type: 'count_distinct',
          stat_val: '22',
        },
        {
          end_epoch: 1571616000,
          start_epoch: 1571616000,
          stat_type: 'count_zero',
          stat_val: '44',
        },
        {
          end_epoch: 1571616000,
          start_epoch: 1571616000,
          stat_type: 'max',
          stat_val: '1237466454',
        },
        {
          end_epoch: 1571616000,
          start_epoch: 1571616000,
          stat_type: 'min',
          stat_val: '856',
        },
        {
          end_epoch: 1571616000,
          start_epoch: 1571616000,
          stat_type: 'avg',
          stat_val: '2356575',
        },
        {
          end_epoch: 1571616000,
          start_epoch: 1571616000,
          stat_type: 'stddev',
          stat_val: '1234563',
        },
      ],
      ...propOverrides,
    };
    const wrapper = shallow<ColumnStats>(<ColumnStats {...props} />);
    return { props, wrapper };
  };

  const { wrapper, props } = setup();
  const instance = wrapper.instance();

  describe('getStatsInfoText', () => {
    it('generates correct info text for a daily partition', () => {
      const startEpoch = 1568160000;
      const endEpoch = 1568160000;
      const expectedInfoText = `Stats reflect data collected on Sep 11, 2019 only. (daily partition)`;
      expect(instance.getStatsInfoText(startEpoch, endEpoch)).toBe(
        expectedInfoText
      );
    });

    it('generates correct info text for a date range', () => {
      const startEpoch = 1568160000;
      const endEpoch = 1571616000;
      const expectedInfoText = `Stats reflect data collected between Sep 11, 2019 and Oct 21, 2019.`;
      expect(instance.getStatsInfoText(startEpoch, endEpoch)).toBe(
        expectedInfoText
      );
    });

    it('generates correct when no dates are given', () => {
      const expectedInfoText = `Stats reflect data collected over a recent period of time.`;
      expect(instance.getStatsInfoText(null, null)).toBe(expectedInfoText);
    });
  });

  describe('renderColumnStat', () => {
    it('renders a single column stat', () => {
      const columnStat = {
        end_epoch: 1571616000,
        start_epoch: 1571616000,
        stat_type: 'count',
        stat_val: '12345',
      };
      const expectedStatType = columnStat.stat_type.toUpperCase();
      const expectedStatValue = columnStat.stat_val;
      const result = shallow(instance.renderColumnStat(columnStat));
      expect(result.find('.stat-name').text()).toBe(expectedStatType);
      expect(result.find('.stat-value').text()).toBe(expectedStatValue);
    });
  });

  describe('render', () => {
    it('calls the appropriate functions', () => {
      const getStatsInfoTextSpy = jest.spyOn(instance, 'getStatsInfoText');
      instance.render();

      expect(getStatsInfoTextSpy).toHaveBeenCalledWith(1571616000, 1571616000);
    });

    it('calls renderColumnStat with all of the stats', () => {
      const renderColumnStatSpy = jest.spyOn(instance, 'renderColumnStat');
      instance.render();
      props.stats.forEach((stat) => {
        expect(renderColumnStatSpy).toHaveBeenCalledWith(stat);
      });
    });
  });
});
