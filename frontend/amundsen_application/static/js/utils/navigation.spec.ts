// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { ResourceType } from 'interfaces/Resources';

import * as NavigationUtils from './navigation';

describe('navigation', () => {
  describe('updateSearchUrl', () => {
    let mockUrl: string;
    let generateSearchUrlSpy: jest.SpyInstance;
    let historyReplaceSpy: jest.SpyInstance;
    let historyPushSpy: jest.SpyInstance;
    let searchParams: Record<string, any>;

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

    afterAll(() => {
      jest.restoreAllMocks();
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

  describe('buildLineageURL', () => {
    it('builds a path to the lineage page from table metadata', () => {
      const mockMetadata = {
        cluster: 'cluster',
        database: 'database',
        schema: 'schema',
        name: 'name',
      };
      const expected = `/lineage/table/cluster/database/schema/name`;
      const actual = NavigationUtils.buildLineageURL(mockMetadata);

      expect(actual).toEqual(expected);
    });
  });

  describe('buildTableKey', () => {
    it('picks up url params and constructs a table key for backed interactions', () => {
      const testMatch = {
        cluster: 'cluster',
        database: 'database',
        schema: 'schema',
        table: 'table',
      };
      const expected = 'database://cluster.schema/table';
      const actual = NavigationUtils.buildTableKey(testMatch);

      expect(actual).toEqual(expected);
    });
  });

  describe('getLoggingParams', () => {
    let searchString;
    let replaceStateSpy;

    beforeAll(() => {
      replaceStateSpy = jest.spyOn(window.history, 'replaceState');
    });

    it('returns the parsed source and index in an object', () => {
      searchString = 'source=test_source&index=10';
      const params = NavigationUtils.getLoggingParams(searchString);

      expect(params.source).toEqual('test_source');
      expect(params.index).toEqual('10');
    });

    it('clears the logging params from the URL, if present', () => {
      const uri = 'testUri';
      const mockFilter = '{"tag":"tagName"}';

      searchString = `uri=${uri}&filters=${mockFilter}&source=test_source&index=10`;
      replaceStateSpy.mockClear();
      NavigationUtils.getLoggingParams(searchString);

      expect(replaceStateSpy).toHaveBeenCalledWith(
        {},
        '',
        `${window.location.origin}${window.location.pathname}?uri=${uri}&filters=${mockFilter}`
      );
    });

    it('does not clear the logging params if they do not exist', () => {
      searchString = '';
      replaceStateSpy.mockClear();
      NavigationUtils.getLoggingParams(searchString);

      expect(replaceStateSpy).not.toHaveBeenCalled();
    });
  });

  describe('getColumnLink', () => {
    it('picks up url params and constructs a url link to a specific column', () => {
      const testParams = {
        cluster: 'cluster',
        database: 'database',
        schema: 'schema',
        table: 'table',
      };
      const expected = `${window.location.origin}/table_detail/cluster/database/schema/table?tab=columns&column=column`;
      const actual = NavigationUtils.getColumnLink(testParams, 'column');

      expect(actual).toEqual(expected);
    });
  });

  describe('setUrlParam', () => {
    const { location } = global.window;

    beforeAll(() => {
      // @ts-ignore
      delete global.window.location;
      // @ts-ignore
      global.window.location = {
        pathname: '/current/path',
        search: '?test=value',
      };
    });

    afterAll(() => {
      global.window.location = location;
    });

    it('updates the URL', () => {
      const historyReplaceSpy = jest.spyOn(
        NavigationUtils.BrowserHistory,
        'replace'
      );
      const expected = 1;

      NavigationUtils.setUrlParam('testKey', 'testValue');
      const actualURL = historyReplaceSpy.mock.calls[0][0] as string;

      expect(actualURL.match('testKey')?.length).toBe(expected);
      expect(actualURL.match('testValue')?.length).toBe(expected);
    });
  });
});
