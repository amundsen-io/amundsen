import axios, { AxiosResponse } from 'axios';

import globalState from 'fixtures/globalState';

import { ResourceType, SearchType } from 'interfaces';

import * as ConfigUtils from 'config/config-utils';
import * as API from '../v0';

jest.mock('axios');

describe('searchResource', () => {
  let axiosMockPost;
  let dashboardEnabledMock;
  let userEnabledMock;
  let mockSearchResponse: AxiosResponse<API.SearchAPI>;
  beforeAll(() => {
    mockSearchResponse = {
      data: {
        msg: 'Success',
        status_code: 200,
        search_term: globalState.search.search_term,
        table: globalState.search.tables,
        user: globalState.search.users,
      },
      status: 200,
      statusText: '',
      headers: {},
      config: {},
    };
    axiosMockPost = jest
      .spyOn(axios, 'post')
      .mockImplementation(() => Promise.resolve(mockSearchResponse));
    userEnabledMock = jest
      .spyOn(ConfigUtils, 'indexUsersEnabled')
      .mockImplementation(() => true);
    dashboardEnabledMock = jest.spyOn(ConfigUtils, 'indexDashboardsEnabled');
  });

  describe('searchResource', () => {
    it('resolves with empty object if dashboard resource search not supported', async () => {
      axiosMockPost.mockClear();
      const pageIndex = 0;
      const resultsPerPage = ConfigUtils.getSearchResultsPerPage();
      const resourceType = [ResourceType.dashboard];
      const term = 'test';
      expect.assertions(2);
      await API.search(
        pageIndex,
        resultsPerPage,
        resourceType,
        term,
        undefined,
        SearchType.FILTER
      ).then((results) => {
        expect(results).toEqual({});
      });
      expect(axiosMockPost).not.toHaveBeenCalled();
    });

    it('resolves with empty object if user resource search not supported', async () => {
      axiosMockPost.mockClear();
      userEnabledMock.mockImplementationOnce(() => false);
      const pageIndex = 0;
      const resultsPerPage = ConfigUtils.getSearchResultsPerPage();
      const resourceType = [ResourceType.user];
      const term = 'test';
      expect.assertions(2);
      await API.search(
        pageIndex,
        resultsPerPage,
        resourceType,
        term,
        undefined,
        SearchType.FILTER
      ).then((results) => {
        expect(results).toEqual({});
      });
      expect(axiosMockPost).not.toHaveBeenCalled();
    });

    describe('if not searching a user resource', () => {
      it('calls axios post with request for a table resource', async () => {
        axiosMockPost.mockClear();
        const pageIndex = 0;
        const resources = [ResourceType.table];
        const searchTerm = 'test';
        const filters = { schema: { value: 'schema_name' } };
        const searchType = SearchType.SUBMIT_TERM;
        const resultsPerPage = ConfigUtils.getSearchResultsPerPage();
        const highlightingOptions = {
          table: {
            enable_highlight: true,
          },
        };
        await API.search(
          pageIndex,
          resultsPerPage,
          resources,
          searchTerm,
          filters,
          searchType
        );
        expect(axiosMockPost).toHaveBeenCalledWith(`${API.BASE_URL}/search`, {
          filters,
          pageIndex,
          resultsPerPage,
          searchTerm,
          searchType,
          resources,
          highlightingOptions,
        });
      });

      it('calls axios post with request for a dashboard resource', async () => {
        axiosMockPost.mockClear();
        dashboardEnabledMock.mockImplementationOnce(() => true);
        const pageIndex = 0;
        const resources = [ResourceType.dashboard];
        const searchTerm = 'test';
        const filters = { name: { value: 'test' } };
        const searchType = SearchType.SUBMIT_TERM;
        const resultsPerPage = ConfigUtils.getSearchResultsPerPage();
        const highlightingOptions = {
          dashboard: {
            enable_highlight: true,
          },
        };
        await API.search(
          pageIndex,
          resultsPerPage,
          resources,
          searchTerm,
          filters,
          searchType
        );
        expect(axiosMockPost).toHaveBeenCalledWith(`${API.BASE_URL}/search`, {
          filters,
          pageIndex,
          resultsPerPage,
          resources,
          searchTerm,
          searchType,
          highlightingOptions,
        });
      });

      it('calls searchHelper with api call response', async () => {
        const searchHelperSpy = jest.spyOn(API, 'searchHelper');
        await API.search(
          0,
          ConfigUtils.getSearchResultsPerPage(),
          [ResourceType.table],
          'test',
          { schema: { value: 'schema_name' } },
          SearchType.FILTER
        );
        expect(searchHelperSpy).toHaveBeenCalledWith(mockSearchResponse);
      });
    });
  });

  describe('searchResourceHelper', () => {
    it('returns expected object', () => {
      expect(API.searchHelper(mockSearchResponse)).toEqual({
        searchTerm: mockSearchResponse.data.search_term,
        table: mockSearchResponse.data.table,
        user: mockSearchResponse.data.user,
      });
    });
  });
});
