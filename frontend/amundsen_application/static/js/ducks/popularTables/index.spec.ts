import { testSaga } from 'redux-saga-test-plan';

import { TableResource } from 'interfaces';

import globalState from 'fixtures/globalState';

import * as API from './api/v0';
import reducer, {
  getPopularTables,
  getPopularTablesFailure,
  getPopularTablesSuccess,
  PopularTablesReducerState,
} from './reducer';
import { getPopularTablesWorker, getPopularTablesWatcher } from './sagas';
import { GetPopularTables } from './types';

describe('popularTables ducks', () => {
  let expectedTables: TableResource[];

  beforeAll(() => {
    expectedTables = globalState.popularTables.popularTables;
  });

  describe('actions', () => {
    it('getPopularTables - returns the action to get popular tables', () => {
      const action = getPopularTables();
      expect(action.type).toBe(GetPopularTables.REQUEST);
    });

    it('getPopularTablesFailure - returns the action to process failure', () => {
      const action = getPopularTablesFailure();
      const { payload } = action;
      expect(action.type).toBe(GetPopularTables.FAILURE);
      expect(payload.tables).toEqual([]);
    });

    it('getPopularTablesSuccess - returns the action to process success', () => {
      const action = getPopularTablesSuccess(expectedTables);
      const { payload } = action;
      expect(action.type).toBe(GetPopularTables.SUCCESS);
      expect(payload.tables).toBe(expectedTables);
    });
  });

  describe('reducer', () => {
    let testState: PopularTablesReducerState;

    beforeAll(() => {
      testState = {
        popularTablesIsLoaded: false,
        popularTables: [],
      };
    });

    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
    });

    it('should handle GetPopularTables.SUCCESS', () => {
      const expected = expectedTables;
      const actual = reducer(testState, getPopularTablesSuccess(expectedTables))
        .popularTables;

      expect(actual).toEqual(expected);
    });

    it('should handle GetPopularTables.FAILURE', () => {
      const expected = {
        popularTables: [],
        popularTablesIsLoaded: true,
      };
      const actual = reducer(testState, getPopularTablesFailure());

      expect(actual).toEqual(expected);
    });
  });

  describe('sagas', () => {
    describe('getPopularTablesWatcher', () => {
      it('takes every GetPopularTables.REQUEST with getPopularTablesWorker', () => {
        testSaga(getPopularTablesWatcher)
          .next()
          .takeEvery(GetPopularTables.REQUEST, getPopularTablesWorker)
          .next()
          .isDone();
      });
    });

    describe('getPopularTablesWorker', () => {
      it('executes flow for returning tables', () => {
        testSaga(getPopularTablesWorker)
          .next()
          .call(API.getPopularTables)
          .next(expectedTables)
          .put(getPopularTablesSuccess(expectedTables))
          .next()
          .isDone();
      });

      it('handles request error', () => {
        testSaga(getPopularTablesWorker)
          .next()
          .throw(new Error())
          .put(getPopularTablesFailure())
          .next()
          .isDone();
      });
    });
  });
});
