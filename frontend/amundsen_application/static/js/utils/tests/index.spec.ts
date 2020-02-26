import * as DateUtils from 'utils/dateUtils';
import * as NavigationUtils from 'utils/navigationUtils';
import * as qs from 'simple-query-string';
import { ResourceType } from 'interfaces/Resources';


describe('navigationUtils', () => {
  describe('updateSearchUrl', () => {

    let historyReplaceSpy;
    let historyPushSpy;
    let searchParams;
    let expectedQueryString;
    beforeAll(() => {
      historyReplaceSpy = jest.spyOn(NavigationUtils.BrowserHistory, 'replace');
      historyPushSpy = jest.spyOn(NavigationUtils.BrowserHistory, 'push');

      searchParams = {
        term: 'test',
        resource: ResourceType.table,
        index: 0,
      };
      expectedQueryString = `/search?${qs.stringify(searchParams)}`;
    });

    it('calls history.replace when replace is true', () => {
      historyReplaceSpy.mockClear();
      historyPushSpy.mockClear();

      const replace = true;
      NavigationUtils.updateSearchUrl(searchParams, replace);

      expect(historyReplaceSpy).toHaveBeenCalledWith(expectedQueryString);
      expect(historyPushSpy).not.toHaveBeenCalled();
    });


    it('calls history.push when replace is false', () => {
      historyReplaceSpy.mockClear();
      historyPushSpy.mockClear();

      const replace = false;
      NavigationUtils.updateSearchUrl(searchParams, replace);

      expect(historyReplaceSpy).not.toHaveBeenCalled();
      expect(historyPushSpy).toHaveBeenCalledWith(expectedQueryString);
    });
  });
});


describe('dateUtils', () => {
  describe('getMomentDate', () => {

    it('parses a timestamp', () => {
      const config = { timestamp: 1580421964000 };
      const moment = DateUtils.getMomentDate(config);
      const dateString = moment.format('MMM DD, YYYY');
      expect(dateString).toEqual('Jan 30, 2020')
    });

    it('parses an epoch timestamp', () => {
      const config = { epochTimestamp: 1580421964 };
      const moment = DateUtils.getMomentDate(config);
      const dateString = moment.format('MMM DD, YYYY');
      expect(dateString).toEqual('Jan 30, 2020')
    });

    it('parses an date string', () => {
      const config = { dateString: "2020-Jan-30", dateStringFormat: "YYYY-MMM-DD" };
      const moment = DateUtils.getMomentDate(config);
      const dateString = moment.format('MMM DD, YYYY');
      expect(dateString).toEqual('Jan 30, 2020')
    });
  });

  describe('formatDate', () => {
    it('formats a date to the default format', () => {
      const config = { timestamp: 1580421964000 };
      const dateString = DateUtils.formatDate(config);
      expect(dateString).toEqual('Jan 30, 2020')
    });
  });

  describe('formatDateTimeShort', () => {
    it('formats a date to the date time short format', () => {
      const config = { timestamp: 1580421964000 };
      const dateString = DateUtils.formatDateTimeShort(config);
      // This test may fail in your IDE if your timezone is not set to GMT
      expect(dateString).toEqual('Jan 30, 2020 10pm GMT')
    });
  });

  describe('formatDateTimeLong', () => {
    const config = { timestamp: 1580421964000 };
      const dateString = DateUtils.formatDateTimeLong(config);
      expect(dateString).toEqual('January 30th 2020 at 10:06:04 pm')
  })
});
