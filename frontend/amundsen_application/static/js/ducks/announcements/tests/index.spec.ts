import { expectSaga, testSaga } from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import { throwError } from 'redux-saga-test-plan/providers';

import { announcementsGet } from '../api/v0';
import reducer, { getAnnouncements, initialState, AnnouncementsReducerState } from '../reducer';
import { getAnnouncementsWatcher, getAnnouncementsWorker } from '../sagas';
import { GetAnnouncements } from '../types';

describe('announcements ducks', () => {
  describe('actions', () => {
    describe('getAnnouncements', () => {
      it('should return action of type GetAnnouncementsRequest', () => {
        expect(getAnnouncements()).toEqual({ type: GetAnnouncements.REQUEST });
      });
    })
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
      expect(reducer(testState, { type: GetAnnouncements.SUCCESS, payload: { posts: expectedPosts }})).toEqual({
        posts: expectedPosts,
      });
    });

    it('should return the initialState if GetAnnouncements.FAILURE', () => {
      expect(reducer(testState, { type: GetAnnouncements.FAILURE, payload: { posts: [] } })).toEqual(initialState);
    });
  });

  describe('sagas', () => {
    describe('getAnnouncementsWatcher', () => {
      it('takes GetAnnouncements.REQUEST with getAnnouncementsWorker', () => {
        testSaga(getAnnouncementsWatcher)
          .next()
          .takeEveryEffect(GetAnnouncements.REQUEST, getAnnouncementsWorker);
      });
    });

    describe('getAnnouncementsWorker', () => {
      it('gets posts', () => {
        const mockPosts = [{ date: '12/31/1999', title: 'Test', html_content: '<div>Test content</div>' }];
        return expectSaga(getAnnouncementsWorker)
          .provide([
            [matchers.call.fn(announcementsGet), mockPosts],
          ])
          .put({
            type: GetAnnouncements.SUCCESS,
            payload: { posts: mockPosts }
          })
          .run();
      });

      it('handles request error', () => {
        return expectSaga(getAnnouncementsWorker)
          .provide([
            [matchers.call.fn(announcementsGet), throwError(new Error())],
          ])
          .put({
            type: GetAnnouncements.FAILURE,
            payload: { posts: [] }
          })
          .run();
      });
    });
  });
});
