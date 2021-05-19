import axios, { AxiosResponse } from 'axios';

import globalState from 'fixtures/globalState';

import { TableResource } from 'interfaces';

import * as API from '../v0';

jest.mock('axios');

describe('getPopularTables', () => {
  let expectedTables: TableResource[];
  let mockGetResponse: AxiosResponse<API.PopularTablesAPI>;

  beforeAll(() => {
    expectedTables = globalState.popularTables.popularTables;
    mockGetResponse = {
      data: {
        results: expectedTables,
        msg: 'Success',
      },
      status: 200,
      statusText: '',
      headers: {},
      config: {},
    };
    jest
      .spyOn(axios, 'get')
      .mockImplementation(() => Promise.resolve(mockGetResponse));
  });

  it('resolves with array of table resources from response.data on success', async () => {
    expect.assertions(1);
    await API.getPopularTables().then((results) => {
      expect(results).toEqual(expectedTables);
    });
  });
});
