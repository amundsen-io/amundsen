import * as DateUtils from 'utils/dateUtils';
import * as NavigationUtils from 'utils/navigationUtils';
import * as qs from 'simple-query-string';
import { ResourceType } from 'interfaces/Resources';


describe('navigationUtils', () => {
  describe('updateSearchUrl', () => {
    let mockUrl;
    let generateSearchUrlSpy;
    let historyReplaceSpy;
    let historyPushSpy;
    let searchParams;

    beforeAll(() => {
      mockUrl = 'testUrl';
      generateSearchUrlSpy = jest.spyOn(NavigationUtils, 'generateSearchUrl').mockReturnValue(mockUrl);
      historyReplaceSpy = jest.spyOn(NavigationUtils.BrowserHistory, 'replace');
      historyPushSpy = jest.spyOn(NavigationUtils.BrowserHistory, 'push');
      searchParams = {
        term: 'test',
        resource: ResourceType.table,
        index: 0,
      };
    });

    it('calls history.replace when replace is true', () => {
      historyReplaceSpy.mockClear();
      historyPushSpy.mockClear();
      NavigationUtils.updateSearchUrl(searchParams, true);

      expect(historyReplaceSpy).toHaveBeenCalledWith(mockUrl);
      expect(historyPushSpy).not.toHaveBeenCalled();
    });

    it('calls history.push when replace is false', () => {
      historyReplaceSpy.mockClear();
      historyPushSpy.mockClear();
      NavigationUtils.updateSearchUrl(searchParams, false);

      expect(historyReplaceSpy).not.toHaveBeenCalled();
      expect(historyPushSpy).toHaveBeenCalledWith(mockUrl);
    });

    it('calls history.push when default replace value is used', () => {
      historyReplaceSpy.mockClear();
      historyPushSpy.mockClear();
      NavigationUtils.updateSearchUrl(searchParams);

      expect(historyReplaceSpy).not.toHaveBeenCalled();
      expect(historyPushSpy).toHaveBeenCalledWith(mockUrl);
    });

    it('calls generateSearchUrl with searchParams', () => {
      generateSearchUrlSpy.mockClear();
      NavigationUtils.updateSearchUrl(searchParams, true);

      expect(generateSearchUrlSpy).toHaveBeenCalledTimes(1);
      expect(generateSearchUrlSpy).toHaveBeenCalledWith(searchParams);
    });

    afterAll(() => {
      generateSearchUrlSpy.mockRestore();
    })
  });

  describe('generaSearchUrl', () => {
    let testResource;
    let searchParams;
    let url;

    it('returns default route if falsy search term and no filters', () => {
      searchParams = {
        term: '',
        resource: ResourceType.table,
        index: 0,
      };
      url = NavigationUtils.generateSearchUrl(searchParams);
      expect(url).toBe(NavigationUtils.DEFAULT_SEARCH_ROUTE);
    });

    it('excludes term from the url if term is falsy', () => {
      testResource = ResourceType.table;
      searchParams = {
        term: '',
        resource: testResource,
        index: 0,
        filters: {
          [testResource]: {'column': 'column_name' }
        }
      };
      url = NavigationUtils.generateSearchUrl(searchParams);
      expect(url.includes('term=')).toBe(false);
    });

    it('excludes filters from the url if no filters', () => {
      searchParams = {
        term: 'test',
        resource: ResourceType.table,
        index: 0,
      };
      url = NavigationUtils.generateSearchUrl(searchParams);
      expect(url.includes('filters=')).toBe(false);
    });

    it('generates expected url for all valid searchParams', () => {
      const testTerm = 'test';
      const testIndex = 0;
      testResource = ResourceType.table;
      searchParams = {
        term: testTerm,
        resource: testResource,
        index: 0,
        filters: {
          [testResource]: { 'column': 'column_name' }
        }
      };
      url = NavigationUtils.generateSearchUrl(searchParams);
      const expectedFilterString = `%7B%22column%22%3A%22column_name%22%7D`;
      const expectedUrl = `/search?term=${testTerm}&resource=${testResource}&index=${testIndex}&filters=${expectedFilterString}`;
      expect(url).toEqual(expectedUrl);
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
