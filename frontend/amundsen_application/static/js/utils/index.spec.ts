import { ResourceType } from 'interfaces/Resources';
import { assert } from 'console';
import { access } from 'fs';
import { sys } from 'typescript';
import * as DateUtils from './dateUtils';
import * as LogUtils from './logUtils';
import * as NavigationUtils from './navigationUtils';
import * as TextUtils from './textUtils';
import * as NumberUtils from './numberUtils';

describe('textUtils', () => {
  describe('convertText', () => {
    it('converts to lower case', () => {
      const actual = TextUtils.convertText(
        'TESt LoWer cASe',
        TextUtils.CaseType.LOWER_CASE
      );
      const expected = 'test lower case';

      expect(actual).toEqual(expected);
    });

    it('converts to sentence case', () => {
      const actual = TextUtils.convertText(
        'tESt sentence cASe',
        TextUtils.CaseType.SENTENCE_CASE
      );
      const expected = 'Test sentence case';

      expect(actual).toEqual(expected);
    });

    it('converts to upper case', () => {
      const actual = TextUtils.convertText(
        'test upper cASe',
        TextUtils.CaseType.UPPER_CASE
      );
      const expected = 'TEST UPPER CASE';

      expect(actual).toEqual(expected);
    });

    it('converts to title case', () => {
      const actual = TextUtils.convertText(
        'tEST title cASe',
        TextUtils.CaseType.TITLE_CASE
      );
      const expected = 'Test Title Case';

      expect(actual).toEqual(expected);
    });
  });
});

describe('numberUtils', () => {
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
    it('get NaN on non numbers', () => {
      const actual = NumberUtils.formatNumber('2020-11-03');
      const expected = 'NaN';

      expect(actual).toEqual(expected);
    });
  });
});

describe('navigationUtils', () => {
  describe('updateSearchUrl', () => {
    let mockUrl;
    let generateSearchUrlSpy;
    let historyReplaceSpy;
    let historyPushSpy;
    let searchParams;

    beforeAll(() => {
      mockUrl = 'testUrl';
      generateSearchUrlSpy = jest
        .spyOn(NavigationUtils, 'generateSearchUrl')
        .mockReturnValue(mockUrl);
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
    });
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
          [testResource]: { column: 'column_name' },
        },
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
          [testResource]: { column: 'column_name' },
        },
      };
      url = NavigationUtils.generateSearchUrl(searchParams);
      const expectedFilterString = `%7B%22column%22%3A%22column_name%22%7D`;
      const expectedUrl = `/search?term=${testTerm}&resource=${testResource}&index=${testIndex}&filters=${expectedFilterString}`;
      expect(url).toEqual(expectedUrl);
    });
  });

  describe('buildDashboardURL', () => {
    it('encodes the passed URI for safe use on the URL bar', () => {
      const testURI = 'product_dashboard://cluster.groupID/dashboardID';
      const expected =
        '/dashboard/product_dashboard%3A%2F%2Fcluster.groupID%2FdashboardID';
      const actual = NavigationUtils.buildDashboardURL(testURI);

      expect(actual).toEqual(expected);
    });
  });
});

describe('dateUtils', () => {
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

describe('logUtils', () => {
  describe('getLoggingParams', () => {
    let searchString;
    let replaceStateSpy;

    beforeAll(() => {
      replaceStateSpy = jest.spyOn(window.history, 'replaceState');
    });

    it('returns the parsed source and index in an object', () => {
      searchString = 'source=test_source&index=10';
      const params = LogUtils.getLoggingParams(searchString);
      expect(params.source).toEqual('test_source');
      expect(params.index).toEqual('10');
    });

    it('clears the logging params from the URL, if present', () => {
      const uri = 'testUri';
      const mockFilter = '{"tag":"tagName"}';
      searchString = `uri=${uri}&filters=${mockFilter}&source=test_source&index=10`;
      replaceStateSpy.mockClear();
      LogUtils.getLoggingParams(searchString);
      expect(replaceStateSpy).toHaveBeenCalledWith(
        {},
        '',
        `${window.location.origin}${window.location.pathname}?uri=${uri}&filters=${mockFilter}`
      );
    });

    it('does not clear the logging params if they do not exist', () => {
      searchString = '';
      replaceStateSpy.mockClear();
      LogUtils.getLoggingParams(searchString);
      expect(replaceStateSpy).not.toHaveBeenCalled();
    });
  });
});
