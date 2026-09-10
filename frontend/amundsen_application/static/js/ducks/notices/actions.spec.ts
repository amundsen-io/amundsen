// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { aNoticeTestData } from 'fixtures/notices/testDataBuilder';

import {
  getNotices,
  getNoticesFailure,
  getNoticesSuccess,
  initialNoticesState,
} from '.';
import { GetNotices } from './types';

import { STATUS_CODES } from '../../constants';

const testData = aNoticeTestData().withTableLandingIssue().build();

describe('notices actions', () => {
  describe('getNotices', () => {
    it('returns the action to get notices', () => {
      const testKey = 'testKey';
      const action = getNotices(testKey);
      const { payload, type } = action;

      expect(type).toBe(GetNotices.REQUEST);
      expect(payload.key).toBe(testKey);
    });
  });

  describe('getNoticesSuccess', () => {
    it('returns the action to process success', () => {
      const testNotices = testData;
      const expectedStatus = STATUS_CODES.OK;
      const action = getNoticesSuccess(testNotices, expectedStatus);
      const { payload, type } = action;

      expect(type).toBe(GetNotices.SUCCESS);
      expect(payload.notices).toEqual(testNotices);
      expect(payload.statusCode).toBe(expectedStatus);
    });
  });

  describe('getNoticesFailure', () => {
    it('returns the action to process failure', () => {
      const expectedStatus = STATUS_CODES.INTERNAL_SERVER_ERROR;
      const expectedMessage = 'oops';
      const action = getNoticesFailure(expectedStatus, expectedMessage);
      const { payload, type } = action;

      expect(type).toBe(GetNotices.FAILURE);
      expect(payload.notices).toEqual(initialNoticesState);
      expect(payload.statusCode).toBe(expectedStatus);
      expect(payload.statusMessage).toBe(expectedMessage);
    });
  });
});
