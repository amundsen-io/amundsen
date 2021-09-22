import axios from 'axios';

import { qualityChecks } from 'fixtures/metadata/table';
import * as API from './v0';

jest.mock('axios');

describe('getTableQualityChecks', () => {
  let axiosMockGet;
  it('resolves with object containing quality checks and status code', async () => {
    const mockStatus = 200;
    const mockResponse = {
      data: {
        checks: qualityChecks,
      },
      status: mockStatus,
    };
    axiosMockGet = jest
      .spyOn(axios, 'get')
      .mockImplementationOnce(() => Promise.resolve(mockResponse));
    expect.assertions(2);
    await API.getTableQualityChecksSummary('testUri').then(
      (processedResponse) => {
        expect(processedResponse).toEqual({
          checks: mockResponse.data.checks,
          status: mockStatus,
        });
      }
    );
    expect(axiosMockGet).toHaveBeenCalled();
  });

  it('catches error and resolves for feature code', async () => {
    const mockStatus = 500;
    const mockResponse = {
      response: {
        status: mockStatus,
      },
    };
    axiosMockGet = jest
      .spyOn(axios, 'get')
      .mockImplementationOnce(() => Promise.reject(mockResponse));
    expect.assertions(2);
    await API.getTableQualityChecksSummary('testUri').catch(
      (processedResponse) => {
        expect(processedResponse).toEqual({
          status: mockStatus,
        });
      }
    );
    expect(axiosMockGet).toHaveBeenCalled();
  });
});
