import axios, { AxiosResponse } from 'axios';

import { AnnouncementPost } from 'interfaces';

import * as API from './v0';

import { STATUS_CODES } from '../../../constants';

jest.mock('axios');

describe('getAnnouncements', () => {
  let expectedPosts: AnnouncementPost[];
  let mockResponse: AxiosResponse<API.AnnouncementsAPI>;

  beforeAll(() => {
    expectedPosts = [
      {
        date: '12/31/1999',
        title: 'Test',
        html_content: '<div>Test content</div>',
      },
    ];
  });

  describe('when success', () => {
    it('resolves with array of posts and status code', async () => {
      expect.assertions(1);

      mockResponse = {
        data: {
          posts: expectedPosts,
          msg: 'Success',
        },
        status: STATUS_CODES.OK,
        statusText: '',
        headers: {},
        // @ts-ignore
        config: {},
      };
      // @ts-ignore: TypeScript errors on Jest mock methods unless we extend AxiosStatic for tests
      axios.mockResolvedValue(mockResponse);

      const expected = {
        posts: expectedPosts,
        statusCode: mockResponse.status,
      };

      await API.getAnnouncements().then((response) => {
        expect(response).toEqual(expected);
      });
    });
  });

  describe('when error', () => {
    it('catches error and resolves with object containing error code', async () => {
      expect.assertions(1);

      mockResponse = {
        data: {
          posts: [],
          msg: 'A client for retrieving announcements must be configured',
        },
        status: STATUS_CODES.INTERNAL_SERVER_ERROR,
        statusText: '',
        headers: {},
        // @ts-ignore
        config: {},
      };
      // @ts-ignore: TypeScript errors on Jest mock methods unless we extend AxiosStatic for tests
      axios.mockRejectedValue(mockResponse);

      const expected = {
        posts: [],
        statusCode: mockResponse.status,
      };

      await API.getAnnouncements().catch((response) => {
        expect(response).toEqual(expected);
      });
    });
  });

  afterAll(() => {
    // @ts-ignore: TypeScript errors on Jest mock methods unless we extend AxiosStatic for tests
    axios.mockClear();
  });
});
