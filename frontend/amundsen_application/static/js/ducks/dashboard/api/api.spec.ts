import axios from 'axios';

import { dashboardMetadata } from 'fixtures/metadata/dashboard';

import * as API from './v0';

import { STATUS_CODES } from '../../../constants';

jest.mock('axios');

describe('getDashboard', () => {
  let axiosMockGet;

  it('resolves with object containing dashboard metadata and status code', async () => {
    const mockStatus = STATUS_CODES.OK;
    const mockResponse = {
      data: {
        dashboard: dashboardMetadata,
        msg: 'success',
      },
      status: mockStatus,
    };

    axiosMockGet = jest
      .spyOn(axios, 'get')
      .mockImplementationOnce(() => Promise.resolve(mockResponse));

    expect.assertions(2);

    await API.getDashboard('testUri').then((processedResponse) => {
      expect(processedResponse).toEqual({
        dashboard: dashboardMetadata,
        statusCode: mockStatus,
      });
    });

    expect(axiosMockGet).toHaveBeenCalled();
  });

  it('catches error and resolves with object containing error information', async () => {
    const mockStatus = STATUS_CODES.INTERNAL_SERVER_ERROR;
    const mockMessage = 'oops';
    const mockResponse = {
      response: {
        data: {
          msg: mockMessage,
        },
        status: mockStatus,
      },
    };

    axiosMockGet = jest
      .spyOn(axios, 'get')
      .mockImplementationOnce(() => Promise.reject(mockResponse));

    expect.assertions(2);

    await API.getDashboard('testUri').catch((processedResponse) => {
      expect(processedResponse).toEqual({
        statusMessage: mockMessage,
        statusCode: mockStatus,
      });
    });

    expect(axiosMockGet).toHaveBeenCalled();
  });
});
