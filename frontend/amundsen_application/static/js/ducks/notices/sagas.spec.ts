// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { testSaga } from 'redux-saga-test-plan';

import { aNoticeTestData } from 'fixtures/notices/testDataBuilder';
import * as API from './api/v0';
import * as Sagas from '.';

import { getNotices, getNoticesFailure, getNoticesSuccess } from '.';
import { GetNotices } from './types';

import { STATUS_CODES } from '../../constants';

const testData = aNoticeTestData().withQualityIssue().build();

describe('notices sagas', () => {
  describe('getNoticesWatcher', () => {
    it('takes every GetNotices.REQUEST with getNoticesWorker', () => {
      testSaga(Sagas.getNoticesWatcher)
        .next()
        .takeEvery(GetNotices.REQUEST, Sagas.getNoticesWorker)
        .next()
        .isDone();
    });
  });

  describe('getNoticesWorker', () => {
    it('executes flow for successfully getting Notices', () => {
      const mockResponse = {
        data: testData,
        statusCode: STATUS_CODES.OK,
      };

      testSaga(Sagas.getNoticesWorker, getNotices('testKey'))
        .next()
        .call(API.getTableNotices, 'testKey')
        .next(mockResponse)
        .put(getNoticesSuccess(mockResponse.data, mockResponse.statusCode))
        .next()
        .isDone();
    });

    it('executes flow for a failed request Notices', () => {
      const mockResponse = {
        statusCode: STATUS_CODES.OK,
        statusMessage: 'oops',
      };

      testSaga(Sagas.getNoticesWorker, getNotices('testKey'))
        .next()
        .call(API.getTableNotices, 'testKey')
        // @ts-ignore
        .throw(mockResponse)
        .put(
          getNoticesFailure(mockResponse.statusCode, mockResponse.statusMessage)
        )
        .next()
        .isDone();
    });
  });
});
