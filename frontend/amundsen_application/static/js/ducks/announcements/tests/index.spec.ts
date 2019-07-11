import { expectSaga, testSaga } from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import { throwError } from 'redux-saga-test-plan/providers';

import * as API from '../api/v0';
import reducer, {
  getAnnouncements, getAnnouncementsFailure, getAnnouncementsSuccess,
  initialState, AnnouncementsReducerState
} from '../reducer';
import { getAnnouncementsWatcher, getAnnouncementsWorker } from '../sagas';
import { GetAnnouncements } from '../types';

describe('announcements ducks', () => {
  describe('actions', () => {
    it('getAnnouncements - returns the action to get all tags', () => {
      const action = getAnnouncements();
      expect(action.type).toBe(GetAnnouncements.REQUEST);
    });

    it('getAnnouncementsFailure - returns the action to process failure', () => {
      const action = getAnnouncementsFailure();
      const { payload } = action;
      expect(action.type).toBe(GetAnnouncements.FAILURE);
      expect(payload.posts).toEqual([]);
    });

    it('getAllTagsSuccess - returns the action to process success', () => {
      const expectedPosts = [{ date: '12/31/1999', title: 'Test', html_content: '<div>Test content</div>' }];
      const action = getAnnouncementsSuccess(expectedPosts);
      const { payload } = action;
      expect(action.type).toBe(GetAnnouncements.SUCCESS);
      expect(payload.posts).toBe(expectedPosts);
    });
  });

  describe('reducer', () => {
    let testState: AnnouncementsReducerState;
    beforeAll(() => {
      testState = {
        posts: [],
      };
    });
    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
    });

    it('should handle GetAnnouncements.SUCCESS', () => {
      const expectedPosts = [{ date: '12/31/1999', title: 'Test', html_content: '<div>Test content</div>' }];
      expect(reducer(testState, getAnnouncementsSuccess(expectedPosts))).toEqual({
        posts: expectedPosts,
      });
    });

    it('should return the initialState if GetAnnouncements.FAILURE', () => {
      expect(reducer(testState, getAnnouncementsFailure())).toEqual(initialState);
    });
  });

  describe('sagas', () => {
    describe('getAnnouncementsWatcher', () => {
      it('takes GetAnnouncements.REQUEST with getAnnouncementsWorker', () => {
        testSaga(getAnnouncementsWatcher)
          .next().takeEvery(GetAnnouncements.REQUEST, getAnnouncementsWorker)
          .next().isDone();
      });
    });

    describe('getAnnouncementsWorker', () => {
      it('gets posts', () => {
        const mockPosts = [{ date: '12/31/1999', title: 'Test', html_content: '<div>Test content</div>' }];
        return expectSaga(getAnnouncementsWorker)
          .provide([
            [matchers.call.fn(API.getAnnouncements), mockPosts],
          ])
          .put(getAnnouncementsSuccess(mockPosts))
          .run();
      });

      it('handles request error', () => {
        return expectSaga(getAnnouncementsWorker)
          .provide([
            [matchers.call.fn(API.getAnnouncements), throwError(new Error())],
          ])
          .put(getAnnouncementsFailure())
          .run();
      });
    });
  });
});
