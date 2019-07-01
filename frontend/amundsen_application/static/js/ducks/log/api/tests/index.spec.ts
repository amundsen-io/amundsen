import axios from 'axios';

import { postActionLog, BASE_URL, ActionLogParams } from '../v0';

jest.mock('axios');

describe('postActionLog', () => {
  let axiosMock;
  let params: ActionLogParams;
  beforeAll(() => {
    axiosMock = jest.spyOn(axios, 'post').mockImplementation(() => Promise.resolve());
    params = {};
    postActionLog(params);
  });

  it('calls axios with expected parameters',() => {
    expect(axiosMock).toHaveBeenCalledWith(BASE_URL, params);
  });

  afterAll(() => {
    axiosMock.mockClear();
  })
});
