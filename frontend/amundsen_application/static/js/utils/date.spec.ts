// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as DateUtils from './date';

jest.mock('config/config-utils', () => ({
  getDateConfiguration: jest.fn(() => ({
    dateTimeLong: 'MMMM Do YYYY [at] h:mm:ss a',
    dateTimeShort: 'MMM DD, YYYY ha z',
    default: 'MMM DD, YYYY',
  })),
}));

describe('date', () => {
  describe('getMomentDate', () => {
    it('parses a timestamp', () => {
      const config = { timestamp: 1580421964000 };
      const moment = DateUtils.getMomentDate(config);
      const dateString = moment.format('MMM DD, YYYY');

      expect(dateString).toEqual('Jan 30, 2020');
    });

    it('parses an epoch timestamp', () => {
      const config = { epochTimestamp: 1580421964 };
      const moment = DateUtils.getMomentDate(config);
      const dateString = moment.format('MMM DD, YYYY');

      expect(dateString).toEqual('Jan 30, 2020');
    });

    it('parses an date string', () => {
      const config = {
        dateString: '2020-Jan-30',
        dateStringFormat: 'YYYY-MMM-DD',
      };
      const moment = DateUtils.getMomentDate(config);
      const dateString = moment.format('MMM DD, YYYY');

      expect(dateString).toEqual('Jan 30, 2020');
    });

    it('throws otherwise', () => {
      const config = {};

      expect(() => {
        // @ts-expect-error We throw an error when no valid configs
        DateUtils.getMomentDate(config);
      }).toThrow();
    });
  });

  describe('formatDate', () => {
    it('formats a date to the default format', () => {
      const config = { timestamp: 1580421964000 };
      const dateString = DateUtils.formatDate(config);

      expect(dateString).toEqual('Jan 30, 2020');
    });
  });

  describe('formatDateTimeShort', () => {
    it('formats a date to the date time short format', () => {
      const config = { timestamp: 1580421964000 };
      const dateString = DateUtils.formatDateTimeShort(config);

      // This test may fail in your IDE if your timezone is not set to GMT
      expect(dateString).toEqual('Jan 30, 2020 10pm GMT');
    });
  });

  describe('formatDateTimeLong', () => {
    const config = { timestamp: 1580421964000 };
    const dateString = DateUtils.formatDateTimeLong(config);

    expect(dateString).toEqual('January 30th 2020 at 10:06:04 pm');
  });
});
