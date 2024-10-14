// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { aNoticeTestData } from 'fixtures/notices/testDataBuilder';
import {
  reducer,
  getNotices,
  getNoticesFailure,
  getNoticesSuccess,
  initialNoticesState,
  NoticesReducerState,
} from '.';

import { STATUS_CODES } from '../../constants';

const testData = aNoticeTestData().withSEVIssue().build();

describe('notices reducer', () => {
  let testState: NoticesReducerState;

  beforeAll(() => {
    testState = {
      isLoading: false,
      statusCode: STATUS_CODES.OK,
      notices: initialNoticesState,
    };
  });

  it('should return the existing state if action is not handled', () => {
    expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
  });

  it('should handle GetNotices.REQUEST', () => {
    expect(reducer(testState, getNotices('testKey'))).toEqual({
      ...testState,
      isLoading: true,
      statusCode: null,
    });
  });

  it('should handle GetNotices.SUCCESS', () => {
    expect(
      reducer(testState, getNoticesSuccess(testData, STATUS_CODES.ACCEPTED))
    ).toEqual({
      isLoading: false,
      statusCode: STATUS_CODES.ACCEPTED,
      notices: testData,
    });
  });

  it('should handle GetNotices.FAILURE', () => {
    expect(
      reducer(
        testState,
        getNoticesFailure(STATUS_CODES.INTERNAL_SERVER_ERROR, 'oops')
      )
    ).toEqual({
      isLoading: false,
      statusCode: STATUS_CODES.INTERNAL_SERVER_ERROR,
      notices: initialNoticesState,
    });
  });
});
