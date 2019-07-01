import axios, { AxiosResponse } from 'axios';

import globalState from 'fixtures/globalState';

import { TableResource } from 'interfaces';

import { metadataPopularTables, PopularTablesAPI } from '../v0';

jest.mock('axios');

describe('metadataPopularTables', () => {
  let axiosMock;
  let expectedTables: TableResource[];
  let mockGetResponse: AxiosResponse<PopularTablesAPI>;
  beforeAll(() => {
    expectedTables = globalState.popularTables;
    mockGetResponse = {
      data: {
       results: expectedTables,
       msg: 'Success'
      },
      status: 200,
      statusText: '',
      headers: {},
      config: {}
    };
    axiosMock = jest.spyOn(axios, 'get').mockImplementation(() => Promise.resolve(mockGetResponse));
  });

  it('resolves with array of table resources from response.data on success', async () => {
    expect.assertions(1);
    await metadataPopularTables().then(results => {
      expect(results).toEqual(expectedTables);
    });
  });
});
