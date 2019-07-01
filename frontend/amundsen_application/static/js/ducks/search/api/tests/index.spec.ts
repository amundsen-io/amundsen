import axios, { AxiosResponse } from 'axios';

import { DashboardSearchResults, TableSearchResults, UserSearchResults } from 'ducks/search/types';

import globalState from 'fixtures/globalState';

import { ResourceType, SearchAllOptions } from 'interfaces';

import { searchResource, searchResourceHelper, SearchAPI, BASE_URL } from '../v0';

jest.mock('axios');

describe('searchResource', () => {
  let axiosMockGet;
  let mockTableResponse: AxiosResponse<SearchAPI>;
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

  it('calls axios get with request for a resource', async () => {
    const pageIndex = 0;
    const resourceType = ResourceType.table;
    const term = 'test';
    await searchResource(pageIndex, resourceType, term);
    expect(axiosMockGet).toHaveBeenCalledWith(`${BASE_URL}/${resourceType}?query=${term}&page_index=${pageIndex}`);
  });

  /*
  TODO: Not set up to test this.
  it('calls searchResourceHelper with resolved results', async () => {
    await searchResource(0, ResourceType.table, 'test');
    expect(searchResourceHelper).toHaveBeenCalledWith(mockTableResponse);
  });
  */

  describe('searchResourceHelper', () => {
    it('returns expected object', () => {
      expect(searchResourceHelper(mockTableResponse)).toEqual({
        searchTerm: mockTableResponse.data.search_term,
        tables: mockTableResponse.data.tables,
        users: mockTableResponse.data.users,
      });
    });
  });
});
