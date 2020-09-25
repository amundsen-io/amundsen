// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { getStatsInfoText } from './utils';

describe('ColumnList utils', () => {
  describe('getStatsInfoText', () => {
    it('generates correct info text for a daily partition', () => {
      const startEpoch = 1568160000;
      const endEpoch = 1568160000;
      const expected = `Stats reflect data collected on Sep 11, 2019 only. (daily partition)`;
      const actual = getStatsInfoText(startEpoch, endEpoch);

      expect(actual).toEqual(expected);
    });

    it('generates correct info text for a date range', () => {
      const startEpoch = 1568160000;
      const endEpoch = 1571616000;
      const expected = `Stats reflect data collected between Sep 11, 2019 and Oct 21, 2019.`;
      const actual = getStatsInfoText(startEpoch, endEpoch);

      expect(actual).toEqual(expected);
    });

    it('generates correct when no dates are given', () => {
      const expected = `Stats reflect data collected over a recent period of time.`;
      const actual = getStatsInfoText();

      expect(actual).toEqual(expected);
    });
  });
});
