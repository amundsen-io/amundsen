// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as ConfigUtils from 'config/config-utils';
import * as StatUtils from './stats';

jest.mock('config/config-utils', () => ({
  getUniqueValueStatTypeName: jest.fn(() => 'distinctValues'),
  getDateConfiguration: jest.fn(() => ({
    dateTimeLong: 'MMMM Do YYYY [at] h:mm:ss a',
    dateTimeShort: 'MMM DD, YYYY ha z',
    default: 'MMM DD, YYYY',
  })),
}));

describe('stats', () => {
  const STATS_WITH_NO_UNIQUE_VALUES = [
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'count_null',
      stat_val: '48.0',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'count_zero',
      stat_val: '0.0',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'approx_distinct_count',
      stat_val: '5.0',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'stddev_value',
      stat_val: '1.1710452355200918',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'median_value',
      stat_val: '4.0',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'min_value',
      stat_val: '4.0',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'avg_value',
      stat_val: '4.622641509433962',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'max_value',
      stat_val: '7.0',
    },
    {
      end_epoch: 1615593600,
      start_epoch: 1613001600,
      stat_type: 'column_usage',
      stat_val: '70',
    },
  ];
  const STATS_WITH_SIX_UNIQUE_VALUES = [
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'count_null',
      stat_val: '48.0',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'count_zero',
      stat_val: '0.0',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'approx_distinct_count',
      stat_val: '5.0',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'stddev_value',
      stat_val: '1.1710452355200918',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'median_value',
      stat_val: '4.0',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'min_value',
      stat_val: '4.0',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'avg_value',
      stat_val: '4.622641509433962',
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'distinctValues',
      stat_val:
        "{'lyft': 162, 'grab': 66, 'unknown': 54, 'null': 48, 'unkown': 18, 'didi': 18}",
    },
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'max_value',
      stat_val: '7.0',
    },
    {
      end_epoch: 1615593600,
      start_epoch: 1613001600,
      stat_type: 'column_usage',
      stat_val: '70',
    },
  ];
  const STRINGIFIED_ARRAY_UNIQUE_VALUES = [
    {
      end_epoch: 1617147150,
      start_epoch: 1616542350,
      stat_type: 'count_null',
      stat_val: '0.0',
    },
    {
      end_epoch: 1617147150,
      start_epoch: 1616542350,
      stat_type: 'count_zero',
      stat_val: '4378016.0',
    },
    {
      end_epoch: 1617147150,
      start_epoch: 1616542350,
      stat_type: 'stddev_value',
      stat_val: '0.5856386084183235',
    },
    {
      end_epoch: 1617147150,
      start_epoch: 1616542350,
      stat_type: 'avg_value',
      stat_val: '0.6695026231618191',
    },
    {
      end_epoch: 1617147150,
      start_epoch: 1616542350,
      stat_type: 'distinctValues',
      stat_val:
        '{1: 5756008, 0: 4450396, 2: 591892, 3: 12948, 4: 424, 5: 40, 11: 16, 7: 12, 6: 8, 9: 8, 8: 4, 10: 4}',
    },
    {
      end_epoch: 1617147150,
      start_epoch: 1616542350,
      stat_type: 'approx_distinct_count',
      stat_val: '13.0',
    },
    {
      end_epoch: 1617147150,
      start_epoch: 1616542350,
      stat_type: 'max_value',
      stat_val: '12.0',
    },
    {
      end_epoch: 1617147150,
      start_epoch: 1616542350,
      stat_type: 'min_value',
      stat_val: '0.0',
    },
    {
      end_epoch: 1617147150,
      start_epoch: 1616542350,
      stat_type: 'median_value',
      stat_val: '0.9907752863495858',
    },
    {
      end_epoch: 1615593600,
      start_epoch: 1613001600,
      stat_type: 'column_usage',
      stat_val: '78',
    },
  ];

  describe('getUniqueValues', () => {
    it('returns an empty array when there is no stats', () => {
      const expected = 0;
      const actual = StatUtils.getUniqueValues([]).length;

      expect(actual).toEqual(expected);
    });

    it('returns an empty array when there is no unique values in the stats', () => {
      const expected = 0;
      const actual = StatUtils.getUniqueValues(
        STATS_WITH_NO_UNIQUE_VALUES
      ).length;

      expect(actual).toEqual(expected);
    });

    describe('when there is one unique value in the stats', () => {
      const STATS_WITH_ONE_UNIQUE_VALUE = [
        {
          end_epoch: 1609522182,
          start_epoch: 1608917382,
          stat_type: 'count_null',
          stat_val: '48.0',
        },
        {
          end_epoch: 1609522182,
          start_epoch: 1608917382,
          stat_type: 'count_zero',
          stat_val: '0.0',
        },
        {
          end_epoch: 1609522182,
          start_epoch: 1608917382,
          stat_type: 'approx_distinct_count',
          stat_val: '5.0',
        },
        {
          end_epoch: 1609522182,
          start_epoch: 1608917382,
          stat_type: 'stddev_value',
          stat_val: '1.1710452355200918',
        },
        {
          end_epoch: 1609522182,
          start_epoch: 1608917382,
          stat_type: 'median_value',
          stat_val: '4.0',
        },
        {
          end_epoch: 1609522182,
          start_epoch: 1608917382,
          stat_type: 'min_value',
          stat_val: '4.0',
        },
        {
          end_epoch: 1609522182,
          start_epoch: 1608917382,
          stat_type: 'avg_value',
          stat_val: '4.622641509433962',
        },
        {
          end_epoch: 1609522182,
          start_epoch: 1608917382,
          stat_type: 'distinctValues',
          stat_val: "{'lyft': 162}",
        },
        {
          end_epoch: 1609522182,
          start_epoch: 1608917382,
          stat_type: 'max_value',
          stat_val: '7.0',
        },
        {
          end_epoch: 1615593600,
          start_epoch: 1613001600,
          stat_type: 'column_usage',
          stat_val: '70',
        },
      ];

      it('returns an array with one element', () => {
        const expected = 1;
        const actual = StatUtils.getUniqueValues(
          STATS_WITH_ONE_UNIQUE_VALUE
        ).length;

        expect(actual).toEqual(expected);
      });

      it('returns an array with one element with a value and count', () => {
        const expectedValue = 'string';
        const actualValue = typeof StatUtils.getUniqueValues(
          STATS_WITH_ONE_UNIQUE_VALUE
        )[0].value;
        const expectedCount = 'number';
        const actualCount = typeof StatUtils.getUniqueValues(
          STATS_WITH_ONE_UNIQUE_VALUE
        )[0].count;

        expect(actualValue).toEqual(expectedValue);
        expect(actualCount).toEqual(expectedCount);
      });
    });

    describe('when there are six unique value in the stats', () => {
      it('returns an array with six elements', () => {
        const expected = 6;
        const actual = StatUtils.getUniqueValues(
          STATS_WITH_SIX_UNIQUE_VALUES
        ).length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when there are unique values as a stringified array', () => {
      it('returns an array with zero elements', () => {
        const expected = 0;
        const actual = StatUtils.getUniqueValues(
          STRINGIFIED_ARRAY_UNIQUE_VALUES
        ).length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when there is no unique value configured', () => {
      it('returns an array with zero element', () => {
        const STATS_WITH_ONE_UNIQUE_VALUE = [
          {
            end_epoch: 1609522182,
            start_epoch: 1608917382,
            stat_type: 'count_null',
            stat_val: '48.0',
          },
        ];
        const expected = 0;

        jest
          .spyOn(ConfigUtils, 'getUniqueValueStatTypeName')
          .mockImplementation(() => undefined);

        const actual = StatUtils.getUniqueValues(
          STATS_WITH_ONE_UNIQUE_VALUE
        ).length;

        expect(actual).toEqual(expected);

        jest.restoreAllMocks();
      });
    });
  });

  describe('filterOutUniqueValues', () => {
    describe('when there is no unique values', () => {
      it('returns the same stat object', () => {
        const expected = STATS_WITH_NO_UNIQUE_VALUES;
        const actual = StatUtils.filterOutUniqueValues(
          STATS_WITH_NO_UNIQUE_VALUES
        );

        expect(actual).toEqual(expected);
      });
    });

    describe('when there are unique values', () => {
      it('returns an object with no unique values', () => {
        jest
          .spyOn(ConfigUtils, 'getUniqueValueStatTypeName')
          .mockImplementation(() => 'distinctValues');
        const expected = STATS_WITH_NO_UNIQUE_VALUES;
        const actual = StatUtils.filterOutUniqueValues(
          STATS_WITH_SIX_UNIQUE_VALUES
        );

        expect(actual).toEqual(expected);
      });
    });
  });

  describe('getStatsInfoText', () => {
    it('generates correct info text for a daily partition', () => {
      const startEpoch = 1568160000;
      const endEpoch = 1568160000;
      const expected = `Stats reflect data collected on Sep 11, 2019 only. (daily partition)`;
      const actual = StatUtils.getStatsInfoText(startEpoch, endEpoch);

      expect(actual).toEqual(expected);
    });

    it('generates correct info text for a date range', () => {
      const startEpoch = 1568160000;
      const endEpoch = 1571616000;
      const expected = `Stats reflect data collected between Sep 11, 2019 and Oct 21, 2019.`;
      const actual = StatUtils.getStatsInfoText(startEpoch, endEpoch);

      expect(actual).toEqual(expected);
    });

    it('generates correct info text when no dates are given', () => {
      const expected = `Stats reflect data collected over a recent period of time.`;
      const actual = StatUtils.getStatsInfoText();

      expect(actual).toEqual(expected);
    });

    it('generates correct info text when only endEpoch is given', () => {
      const startEpoch = 0;
      const endEpoch = 1571616000;
      const expected = `Stats reflect data collected until Oct 21, 2019.`;
      const actual = StatUtils.getStatsInfoText(startEpoch, endEpoch);

      expect(actual).toEqual(expected);
    });
  });
});
