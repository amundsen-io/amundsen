import axios, { AxiosResponse } from 'axios';

import globalState from 'fixtures/globalState';

import { PopularResource, ResourceDict } from 'interfaces';

import * as API from '../v0';

import { STATUS_CODES } from '../../../../constants';

jest.mock('axios');

describe('getPopularTables', () => {
  let expectedResources: ResourceDict<PopularResource[]>;
  let mockGetResponse: AxiosResponse<API.PopularTablesAPI>;

  beforeAll(() => {
    expectedResources = globalState.popularResources.popularResources;
    mockGetResponse = {
      data: {
        results: expectedResources,
        msg: 'Success',
      },
      status: STATUS_CODES.OK,
      statusText: '',
      headers: {},
      // @ts-ignore
      config: {},
    };
    jest
      .spyOn(axios, 'get')
      .mockImplementation(() => Promise.resolve(mockGetResponse));
  });

  it('resolves with array of table resources from response.data on success', async () => {
    expect.assertions(1);

    await API.getPopularResources().then((results) => {
      expect(results).toEqual(expectedResources);
    });
  });
});
