import axios from 'axios';

import { featureCode, featureMetadata } from 'fixtures/metadata/feature';

import * as API from './v0';

import { STATUS_CODES } from '../../../constants';

jest.mock('axios');

describe('getFeature', () => {
  let axiosMockGet;

  it('resolves with object containing feature metadata and status code', async () => {
    const mockStatus = STATUS_CODES.OK;
    const mockResponse = {
      data: {
        featureData: featureMetadata,
        msg: 'success',
      },
      status: mockStatus,
    };

    axiosMockGet = jest
      .spyOn(axios, 'get')
      .mockImplementationOnce(() => Promise.resolve(mockResponse));

    expect.assertions(2);

    await API.getFeature('testUri').then((processedResponse) => {
      expect(processedResponse).toEqual({
        feature: featureMetadata,
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

    await API.getFeature('testUri').catch((processedResponse) => {
      expect(processedResponse).toEqual({
        statusMessage: mockMessage,
        statusCode: mockStatus,
      });
    });

    expect(axiosMockGet).toHaveBeenCalled();
  });
});

describe('getFeatureCode', () => {
  let axiosMockGet;

  it('resolves with object containing feature code and status code', async () => {
    const mockStatus = STATUS_CODES.OK;
    const mockResponse = {
      data: featureCode,
      status: mockStatus,
    };

    axiosMockGet = jest
      .spyOn(axios, 'get')
      .mockImplementationOnce(() => Promise.resolve(mockResponse));

    expect.assertions(2);

    await API.getFeatureCode('testUri').then((processedResponse) => {
      expect(processedResponse).toEqual({
        featureCode: mockResponse.data,
        statusCode: mockStatus,
      });
    });

    expect(axiosMockGet).toHaveBeenCalled();
  });

  it('catches error and resolves for feature code', async () => {
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

    await API.getFeatureCode('testUri').catch((processedResponse) => {
      expect(processedResponse).toEqual({
        statusMessage: mockMessage,
        statusCode: mockStatus,
      });
    });

    expect(axiosMockGet).toHaveBeenCalled();
  });
});
