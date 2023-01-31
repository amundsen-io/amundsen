import { aNoticeTestData } from 'fixtures/metadata/notices';

import {
  getNotices,
  getNoticesFailure,
  getNoticesSuccess,
  initialNoticesState,
} from '.';
import { GetNotices } from './types';

const testData = aNoticeTestData().withQualityIssue().build();

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
      const expectedStatus = 200;
      const action = getNoticesSuccess(testNotices, expectedStatus);
      const { payload, type } = action;

      expect(type).toBe(GetNotices.SUCCESS);
      expect(payload.notices).toEqual(testNotices);
      expect(payload.statusCode).toBe(expectedStatus);
    });
  });

  describe('getNoticesFailure', () => {
    it('returns the action to process failure', () => {
      const expectedStatus = 500;
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
