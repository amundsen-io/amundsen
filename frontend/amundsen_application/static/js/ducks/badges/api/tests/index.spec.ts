import axios, { AxiosResponse } from 'axios';

import { Badge } from 'interfaces';

import * as API from '../v0';

describe('getAllBadges', () => {
  it('resolves with array of sorted result of response.data.badges on success', async () => {
    const rawBadges: Badge[] = [
      { badge_name: 'test', category: 'test_c1' },
      { badge_name: 'a_test', category: 'test_c2' },
    ];
    const expectedBadges: Badge[] = [
      { badge_name: 'a_test', category: 'test_c2' },
      { badge_name: 'test', category: 'test_c1' },
    ];
    const mockResponse: AxiosResponse<API.AllBadgesAPI> = {
      data: {
        badges: rawBadges,
        msg: 'Success',
      },
      status: 200,
      statusText: '',
      headers: {},
      config: {},
    };

    jest
      .spyOn(axios, 'get')
      .mockImplementation(() => Promise.resolve(mockResponse));

    expect.assertions(1);

    await API.getAllBadges().then((sortedBadges) => {
      expect(sortedBadges).toEqual(expectedBadges);
    });
  });
});
