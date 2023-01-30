// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import axios from 'axios';

import { aNoticeTestData } from 'fixtures/metadata/notices';

import * as API from './v0';

jest.mock('axios');

const testData = aNoticeTestData().withQualityIssue().build();

describe('getTableNotices', () => {
  let axiosMockGet;

  it('resolves with object containing the table notices and status code', async () => {
    const mockStatus = 200;
    const mockResponse = {
      data: testData,
      status: mockStatus,
    };

    axiosMockGet = jest
      .spyOn(axios, 'get')
      .mockImplementationOnce(() => Promise.resolve(mockResponse));

    expect.assertions(2);

    await API.getTableNotices('database://cluster.schema/table_name').then(
      (processedResponse) => {
        expect(processedResponse).toEqual({
          data: testData,
          statusCode: mockStatus,
        });
      }
    );

    expect(axiosMockGet).toHaveBeenCalled();
  });

  it('catches error and resolves with object containing error information', async () => {
    const mockStatus = 500;
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

    await API.getTableNotices('testUri').catch((processedResponse) => {
      expect(processedResponse).toEqual({
        statusCode: mockStatus,
        statusMessage: mockMessage,
      });
    });

    expect(axiosMockGet).toHaveBeenCalled();
  });
});
