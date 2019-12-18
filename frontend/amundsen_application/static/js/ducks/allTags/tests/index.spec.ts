import { expectSaga, testSaga } from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import { throwError } from 'redux-saga-test-plan/providers';

import * as API from '../api/v0';
import reducer, {
  getAllTags, getAllTagsFailure, getAllTagsSuccess,
  initialState, AllTagsReducerState
} from '../reducer';
import { getAllTagsWatcher, getAllTagsWorker } from '../sagas';
import { GetAllTags } from '../types';

describe('allTags ducks', () => {
  describe('actions', () => {
    it('getAllTags - returns the action to get all tags', () => {
      const action = getAllTags();
      expect(action.type).toEqual(GetAllTags.REQUEST);
    });

    it('getAllTagsFailure - returns the action to process failure', () => {
      const action = getAllTagsFailure();
      const { payload } = action;
      expect(action.type).toBe(GetAllTags.FAILURE);
      expect(payload.allTags).toEqual([]);
    });

    it('getAllTagsSuccess - returns the action to process success', () => {
      const expectedTags = [{tag_count: 2, tag_name: 'test'}, {tag_count: 1, tag_name: 'test2'}];
      const action = getAllTagsSuccess(expectedTags);
      const { payload } = action;
      expect(action.type).toBe(GetAllTags.SUCCESS);
      expect(payload.allTags).toBe(expectedTags);
    });
  });

  describe('reducer', () => {
    let testState: AllTagsReducerState;
    beforeAll(() => {
      testState = {
        allTags: [],
        isLoading: true,
      };
    });
    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
    });

    it('should handle GetAllTags.REQUEST', () => {
      expect(reducer(testState, getAllTags())).toEqual({
        allTags: [],
        isLoading: true,
      });
    });

    it('should handle GetAllTags.SUCCESS', () => {
      const expectedTags = [{tag_count: 2, tag_name: 'test'}, {tag_count: 1, tag_name: 'test2'}];
      expect(reducer(testState, getAllTagsSuccess(expectedTags))).toEqual({
        allTags: expectedTags,
        isLoading: false,
      });
    });

    it('should return the initialState if GetAllTags.FAILURE', () => {
      expect(reducer(testState, getAllTagsFailure())).toEqual(initialState);
    });
  });

  describe('sagas', () => {
    describe('getAllTagsWatcher', () => {
      it('takes GetAllTags.REQUEST with getAllTagsWorker', () => {
        testSaga(getAllTagsWatcher)
          .next().takeEvery(GetAllTags.REQUEST, getAllTagsWorker)
          .next().isDone();
      });
    });

    describe('getAllTagsWorker', () => {
      it('gets allTags', () => {
        const mockTags = [{tag_count: 2, tag_name: 'test'}, {tag_count: 1, tag_name: 'test2'}];
        return expectSaga(getAllTagsWorker)
          .provide([
            [matchers.call.fn(API.getAllTags), mockTags],
          ])
          .put(getAllTagsSuccess(mockTags))
          .run();
      });

      it('handles request error', () => {
        return expectSaga(getAllTagsWorker)
          .provide([
            [matchers.call.fn(API.getAllTags), throwError(new Error())],
          ])
          .put(getAllTagsFailure())
          .run();
      });
    });
  });
});
