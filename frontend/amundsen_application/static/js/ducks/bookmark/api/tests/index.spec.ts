import axios from 'axios';

import { ResourceType } from 'interfaces';

import * as API from '../v0';

import { STATUS_CODES } from '../../../../constants';

jest.mock('axios');

describe('addBookmark', () => {
  let mockPutResponse;
  let axiosMock;

  beforeAll(() => {
    mockPutResponse = {
      data: {
        bookmarks: [],
        msg: 'Success',
      },
      status: STATUS_CODES.OK,
      statusText: '',
      headers: {},
      config: {},
    };
    axiosMock = jest
      .spyOn(axios, 'put')
      .mockImplementation(() => Promise.resolve(mockPutResponse));
  });

  it('calls axios with correct parameters', async () => {
    expect.assertions(1);

    const givenResource = ResourceType.table;

    await API.addBookmark('test', givenResource).then(() => {
      expect(axiosMock).toHaveBeenCalledWith(`${API.API_PATH}/user/bookmark`, {
        type: givenResource,
        key: 'test',
      });
    });
  });

  it('returns response data', async () => {
    expect.assertions(1);

    const givenResource = ResourceType.table;

    await API.addBookmark('test', givenResource).then((data) => {
      expect(data).toEqual(mockPutResponse.data);
    });
  });

  afterAll(() => {
    axiosMock.mockClear();
  });
});

describe('getBookmarks', () => {
  let mockGetResponse;
  let axiosMock;

  beforeAll(() => {
    mockGetResponse = {
      data: {
        bookmarks: [],
        msg: 'Success',
      },
      status: STATUS_CODES.OK,
      statusText: '',
      headers: {},
      config: {},
    };
    axiosMock = jest
      .spyOn(axios, 'get')
      .mockImplementation(() => Promise.resolve(mockGetResponse));
  });

  it('calls axios with correct parameters if userId provided', async () => {
    expect.assertions(1);

    await API.getBookmarks('testUserId').then(() => {
      expect(axiosMock).toHaveBeenCalledWith(
        `${API.API_PATH}/user/bookmark?user_id=testUserId`
      );
    });
  });

  it('calls axios with correct parameters if userId not provided', async () => {
    expect.assertions(1);

    await API.getBookmarks().then(() => {
      expect(axiosMock).toHaveBeenCalledWith(`${API.API_PATH}/user/bookmark`);
    });
  });

  it('returns response data', async () => {
    expect.assertions(1);

    await API.getBookmarks('testUserId').then((data) => {
      expect(data).toEqual(mockGetResponse.data);
    });
  });

  afterAll(() => {
    axiosMock.mockClear();
  });
});

describe('removeBookmark', () => {
  let mockDeleteResponse;
  let axiosMock;

  beforeAll(() => {
    mockDeleteResponse = {
      data: {
        resourceKey: 'test',
        resourceType: 'table',
        msg: 'Success',
      },
      status: STATUS_CODES.OK,
      statusText: '',
      headers: {},
      config: {},
    };
    axiosMock = jest
      .spyOn(axios, 'delete')
      .mockImplementation(() => Promise.resolve(mockDeleteResponse));
  });

  it('calls axios with correct parameters', async () => {
    expect.assertions(1);

    const givenResource = ResourceType.table;

    await API.removeBookmark('testKey', givenResource).then(() => {
      expect(axiosMock).toHaveBeenCalledWith(`${API.API_PATH}/user/bookmark`, {
        data: { type: givenResource, key: 'testKey' },
      });
    });
  });

  it('returns response data', async () => {
    expect.assertions(1);

    const givenResource = ResourceType.table;

    await API.removeBookmark('test', givenResource).then((data) => {
      expect(data).toEqual(mockDeleteResponse.data);
    });
  });

  afterAll(() => {
    axiosMock.mockClear();
  });
});
