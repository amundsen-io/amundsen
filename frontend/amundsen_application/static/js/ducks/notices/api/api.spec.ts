// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import axios from 'axios';

import { aNoticeTestData } from 'fixtures/notices/testDataBuilder';

import * as API from './v0';

import { STATUS_CODES } from '../../../constants';

jest.mock('axios');

const testData = aNoticeTestData().withDAGIssue().build();

describe('getTableNotices', () => {
  let axiosMockGet;

  it('resolves with object containing the table notices and status code', async () => {
    const mockStatus = STATUS_CODES.OK;
    const mockResponse = {
      data: {
        msg: 'Success',
        notices: testData,
      },
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

    await API.getTableNotices('testUri').catch((processedResponse) => {
      expect(processedResponse).toEqual({
        statusCode: mockStatus,
        statusMessage: mockMessage,
      });
    });

    expect(axiosMockGet).toHaveBeenCalled();
  });
});
