import axios, { AxiosResponse } from 'axios';

import globalState from 'fixtures/globalState';

import { LoggedInUser, PeopleUser, Resource } from 'interfaces';

import {
  loggedInUser, userById, userOwn, userRead,
  LoggedInUserAPI, UserAPI, UserOwnAPI, UserReadAPI
} from '../v0';

jest.mock('axios');

describe('loggedInUser', () => {
  let axiosMock;
  let mockGetResponse: AxiosResponse<LoggedInUserAPI>;
  let testUser: LoggedInUser;
  beforeAll(() => {
    testUser = globalState.user.loggedInUser;
    mockGetResponse = {
      data: {
       user: testUser,
       msg: 'Success'
      },
      status: 200,
      statusText: '',
      headers: {},
      config: {}
    };
    axiosMock = jest.spyOn(axios, 'get').mockImplementation(() => Promise.resolve(mockGetResponse));
  });

  it('calls axios with correct parameters', async () => {
    expect.assertions(1);
    await loggedInUser().then(user => {
      expect(axiosMock).toHaveBeenCalledWith(`/api/auth_user`);
    });
  });

  it('returns user from response data', async () => {
    expect.assertions(1);
    await loggedInUser().then(user => {
      expect(user).toBe(testUser);
    });
  });

  afterAll(() => {
    axiosMock.mockClear();
  })
});

describe('userById', () => {
  let axiosMock;
  let mockGetResponse: AxiosResponse<UserAPI>;
  let testId: string;
  let testUser: PeopleUser;
  beforeAll(() => {
    testId = 'testId';
    testUser = globalState.user.profile.user;
    mockGetResponse = {
      data: {
       user: testUser,
       msg: 'Success'
      },
      status: 200,
      statusText: '',
      headers: {},
      config: {}
    };
    axiosMock = jest.spyOn(axios, 'get').mockImplementation(() => Promise.resolve(mockGetResponse));
  });

  it('calls axios with correct parameters', async () => {
    expect.assertions(1);
    await userById(testId).then(user => {
      expect(axiosMock).toHaveBeenCalledWith(`/api/metadata/v0/user?user_id=${testId}`);
    });
  });

  it('returns user from response data', async () => {
    expect.assertions(1);
    await userById(testId).then(user => {
      expect(user).toBe(testUser);
    });
  });

  afterAll(() => {
    axiosMock.mockClear();
  })
});

describe('userOwn', () => {
  let axiosMock;
  let mockGetResponse: AxiosResponse<UserOwnAPI>;
  let testId: string;
  let testResources: Resource[];
  beforeAll(() => {
    testId = 'testId';
    testResources = globalState.user.profile.own;
    mockGetResponse = {
      data: {
       own: testResources,
       msg: 'Success'
      },
      status: 200,
      statusText: '',
      headers: {},
      config: {}
    };
    axiosMock = jest.spyOn(axios, 'get').mockImplementation(() => Promise.resolve(mockGetResponse));
  });

  it('calls axios with correct parameters', async () => {
    expect.assertions(1);
    await userOwn(testId).then(data => {
      expect(axiosMock).toHaveBeenCalledWith(`/api/metadata/v0/user/own?user_id=${testId}`);
    });
  });

  it('returns response data with owned resources', async () => {
    expect.assertions(1);
    await userOwn(testId).then(data => {
      expect(data.own).toBe(testResources);
    });
  });

  afterAll(() => {
    axiosMock.mockClear();
  })
});

describe('userRead', () => {
  let axiosMock;
  let mockGetResponse: AxiosResponse<UserReadAPI>;
  let testId: string;
  let testResources: Resource[];
  beforeAll(() => {
    testId = 'testId';
    testResources = globalState.user.profile.read;
    mockGetResponse = {
      data: {
       read: testResources,
       msg: 'Success'
      },
      status: 200,
      statusText: '',
      headers: {},
      config: {}
    };
    axiosMock = jest.spyOn(axios, 'get').mockImplementation(() => Promise.resolve(mockGetResponse));
  });

  it('calls axios with correct parameters', async () => {
    expect.assertions(1);
    await userRead(testId).then(data => {
      expect(axiosMock).toHaveBeenCalledWith(`/api/metadata/v0/user/read?user_id=${testId}`);
    });
  });

  it('returns response data with frequently read resources', async () => {
    expect.assertions(1);
    await userRead(testId).then(data => {
      expect(data.read).toBe(testResources);
    });
  });

  afterAll(() => {
    axiosMock.mockClear();
  })
});
