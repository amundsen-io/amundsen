import axios, { AxiosResponse } from 'axios';

import { AnnouncementPost } from 'interfaces';

import * as API from '../v0';

jest.mock('axios');

describe('getAnnouncements', () => {
  let expectedPosts: AnnouncementPost[];
  let mockResponse: AxiosResponse<API.AnnouncementsAPI>;
  beforeAll(() => {
    expectedPosts = [{ date: '12/31/1999', title: 'Test', html_content: '<div>Test content</div>' }];
    mockResponse = {
      data: {
       posts: expectedPosts,
       msg: 'Success'
      },
      status: 200,
      statusText: '',
      headers: {},
      config: {}
    };
    // @ts-ignore: TypeScript errors on Jest mock methods unless we extend AxiosStatic for tests
    axios.mockResolvedValue(mockResponse);
  });

  it('resolves with array of posts from response.data on success', async () => {
    expect.assertions(1);
    await API.getAnnouncements().then(posts => {
      expect(posts).toEqual(expectedPosts);
    });
  });

  afterAll(() => {
    // @ts-ignore: TypeScript errors on Jest mock methods unless we extend AxiosStatic for tests
    axios.mockClear();
  })
});
