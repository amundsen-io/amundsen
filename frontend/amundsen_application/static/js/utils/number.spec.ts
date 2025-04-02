// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as ConfigUtils from 'config/config-utils';
import * as NumberUtils from './number';

jest.mock('config/config-utils', () => ({
  getNumberFormat: jest.fn(() => null),
}));

describe('number', () => {
  describe('isNumber', () => {
    it('returns true if string is number', () => {
      const actual = NumberUtils.isNumber('1234');
      const expected = true;

      expect(actual).toEqual(expected);
    });

    it('returns false if string is not number', () => {
      const actualString = NumberUtils.isNumber('abcd');
      const actualDate = NumberUtils.isNumber('2020-11-03');
      const actualAlphaNum = NumberUtils.isNumber('1a2b3c');
      const expected = false;

      expect(actualString).toEqual(expected);
      expect(actualDate).toEqual(expected);
      expect(actualAlphaNum).toEqual(expected);
    });
  });

  describe('formatNumber', () => {
    it('returns formatted number', () => {
      const actual = NumberUtils.formatNumber('1998');
      const expected = '1,998';

      expect(actual).toEqual(expected);
    });

    describe('when a non-number is passed', () => {
      it('returns NaN', () => {
        const actual = NumberUtils.formatNumber('2020-11-03');
        const expected = 'NaN';

        expect(actual).toEqual(expected);
      });
    });

    describe('when numberSystem is set', () => {
      it('returns formatted number', () => {
        jest.spyOn(ConfigUtils, 'getNumberFormat').mockImplementation(() => ({
          numberSystem: 'de-DE',
        }));
        const testNumber = 123456.789;
        const actual = NumberUtils.formatNumber(testNumber);
        const expected = '123,456.789';

        expect(actual).toEqual(expected);
      });
    });

    describe('when numberSystem is null', () => {
      it('returns formatted number', () => {
        jest.spyOn(ConfigUtils, 'getNumberFormat').mockImplementation(() => ({
          numberSystem: null,
        }));
        const testNumber = 123456.789;
        const actual = NumberUtils.formatNumber(testNumber);
        const expected = '123,456.789';

        expect(actual).toEqual(expected);
      });
    });
  });
});
