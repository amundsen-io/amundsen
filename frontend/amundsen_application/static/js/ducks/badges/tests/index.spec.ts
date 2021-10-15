import { expectSaga, testSaga } from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import { throwError } from 'redux-saga-test-plan/providers';

import * as API from '../api/v0';
import reducer, {
  getAllBadges,
  getAllBadgesFailure,
  getAllBadgesSuccess,
  initialState,
  BadgesReducerState,
} from '../reducer';

import { getAllBadgesWatcher, getAllBadgesWorker } from '../sagas';
import { GetAllBadges } from '../types';

describe('allBadges ducks', () => {
  describe('actions', () => {
    it('getAllBadges - returns the action to get all badges', () => {
      const action = getAllBadges();
      expect(action.type).toEqual(GetAllBadges.REQUEST);
    });

    it('getAllBadgesFailure - returns the action to process failure', () => {
      const action = getAllBadgesFailure();
      const { payload } = action;
      expect(action.type).toBe(GetAllBadges.FAILURE);
      expect(payload.allBadges).toEqual([]);
    });

    it('getAllBadgesSuccess - returns the action to process success', () => {
      const expectedBadges = [
        { badge_count: 2, badge_name: 'test' },
        { badge_count: 1, badge_name: 'test2' },
      ];
      const action = getAllBadgesSuccess(expectedBadges);
      const { payload } = action;
      expect(action.type).toBe(GetAllBadges.SUCCESS);
      expect(payload.allBadges).toBe(expectedBadges);
    });
  });

  describe('reducer', () => {
    let testState: BadgesReducerState;
    beforeAll(() => {
      testState = {
        allBadges: {
          isLoading: true,
          badges: [],
        },
      };
    });
    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
    });

    it('should handle GetAllBadges.REQUEST', () => {
      expect(reducer(testState, getAllBadges())).toEqual({
        allBadges: {
          isLoading: true,
          badges: [],
        },
      });
    });

    it('should handle GetAllBadges.SUCCESS', () => {
      const expectedBadges = [
        { category: 'test_c1', badge_name: 'test1' },
        { category: 'test_c2', badge_name: 'test2' },
      ];
      expect(reducer(testState, getAllBadgesSuccess(expectedBadges))).toEqual({
        allBadges: {
          isLoading: false,
          badges: expectedBadges,
        },
      });
    });

    it('should return the initialState if GetAllBadges.FAILURE', () => {
      expect(reducer(testState, getAllBadgesFailure())).toEqual(initialState);
    });
  });

  describe('sagas', () => {
    describe('getAllBadgesWatcher', () => {
      it('takes GetAllBadges.REQUEST with getAllBadgesWorker', () => {
        testSaga(getAllBadgesWatcher)
          .next()
          .takeEvery(GetAllBadges.REQUEST, getAllBadgesWorker)
          .next()
          .isDone();
      });
    });

    describe('getAllBadgesWorker', () => {
      it('gets allBadges', () => {
        const mockBadges = [
          { category: 'test_c1', badge_name: 'test1' },
          { category: 'test_c2', badge_name: 'test2' },
        ];
        return expectSaga(getAllBadgesWorker)
          .provide([[matchers.call.fn(API.getAllBadges), mockBadges]])
          .put(getAllBadgesSuccess(mockBadges))
          .run();
      });

      it('handles request error', () =>
        expectSaga(getAllBadgesWorker)
          .provide([
            [matchers.call.fn(API.getAllBadges), throwError(new Error())],
          ])
          .put(getAllBadgesFailure())
          .run());
    });
  });
});
