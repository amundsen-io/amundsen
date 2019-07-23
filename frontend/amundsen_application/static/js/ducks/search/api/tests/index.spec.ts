import axios, { AxiosResponse } from 'axios';

import AppConfig from 'config/config';

import { DashboardSearchResults, TableSearchResults, UserSearchResults } from 'ducks/search/types';

import globalState from 'fixtures/globalState';

import { ResourceType } from 'interfaces';

import * as API from '../v0';

jest.mock('axios');



describe('searchResource', () => {
  let axiosMockGet;
  let mockTableResponse: AxiosResponse<API.SearchAPI>;
  beforeAll(() => {
    mockTableResponse = {
      data: {
        msg: 'Success',
        status_code: 200,
        search_term: globalState.search.search_term,
        tables: globalState.search.tables,
        users: globalState.search.users,
      },
      status: 200,
      statusText: '',
      headers: {},
      config: {},
    };
    axiosMockGet = jest.spyOn(axios, 'get').mockImplementation(() => Promise.resolve(mockTableResponse));
  });

  describe('searchResource', () => {
    it('calls axios get with request for a resource', async () => {
      axiosMockGet.mockClear();
      const pageIndex = 0;
      const resourceType = ResourceType.table;
      const term = 'test';
      await API.searchResource(pageIndex, resourceType, term);
      expect(axiosMockGet).toHaveBeenCalledWith(`${API.BASE_URL}/${resourceType}?query=${term}&page_index=${pageIndex}`);
    });

    it('calls searchResourceHelper with api call response', async () => {
      const searchResourceHelperSpy = jest.spyOn(API, 'searchResourceHelper');
      await API.searchResource(0, ResourceType.table, 'test');
      expect(searchResourceHelperSpy).toHaveBeenCalledWith(mockTableResponse);
    });

    it('resolves with empty object if dashboard resource search not supported', async () => {
      axiosMockGet.mockClear();
      const pageIndex = 0;
      const resourceType = ResourceType.dashboard;
      const term = 'test';
      expect.assertions(2);
      await API.searchResource(pageIndex, resourceType, term).then(results => {
        expect(results).toEqual({});
      });
      expect(axiosMockGet).not.toHaveBeenCalled();
    });

    it('resolves with empty object if user resource search not supported', async () => {
      axiosMockGet.mockClear();
      AppConfig.indexUsers.enabled = false;
      const pageIndex = 0;
      const resourceType = ResourceType.user;
      const term = 'test';
      expect.assertions(2);
      await API.searchResource(pageIndex, resourceType, term).then(results => {
        expect(results).toEqual({});
      });
      expect(axiosMockGet).not.toHaveBeenCalled();
    });
  });

  describe('searchResourceHelper', () => {
    it('returns expected object', () => {
      expect(API.searchResourceHelper(mockTableResponse)).toEqual({
        searchTerm: mockTableResponse.data.search_term,
        tables: mockTableResponse.data.tables,
        users: mockTableResponse.data.users,
      });
    });
  });
});
