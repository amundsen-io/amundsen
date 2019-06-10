import { expectSaga, testSaga } from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import { throwError } from 'redux-saga-test-plan/providers';

import { metadataAllTags } from '../api/v0';
import reducer, { getAllTags, initialState, AllTagsReducerState } from '../reducer';
import { getAllTagsWatcher, getAllTagsWorker } from '../sagas';
import { GetAllTags } from '../types';

describe('allTags ducks', () => {
  describe('actions', () => {
    describe('getAllTags', () => {
      it('should return action of type GetAllTagsRequest', () => {
        expect(getAllTags()).toEqual({ type: GetAllTags.REQUEST });
      });
    })
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
      expect(reducer(testState, { type: GetAllTags.REQUEST })).toEqual({
        allTags: [],
        isLoading: true,
      });
    });

    it('should handle GetAllTags.SUCCESS', () => {
      const expectedTags = [{tag_count: 2, tag_name: 'test'}, {tag_count: 1, tag_name: 'test2'}];
      expect(reducer(testState, { type: GetAllTags.SUCCESS, payload: { tags: expectedTags }})).toEqual({
        allTags: expectedTags,
        isLoading: false,
      });
    });

    it('should return the initialState if GetAllTags.FAILURE', () => {
      expect(reducer(testState, { type: GetAllTags.FAILURE, payload: { tags: [] } })).toEqual(initialState);
    });
  });

  describe('sagas', () => {
    describe('getAllTagsWatcher', () => {
      it('takes GetAllTags.REQUEST with getAllTagsWorker', () => {
        testSaga(getAllTagsWatcher)
          .next()
          .takeEveryEffect(GetAllTags.REQUEST, getAllTagsWorker);
      });
    });

    describe('getAllTagsWorker', () => {
      it('gets allTags', () => {
        const mockTags = [{tag_count: 2, tag_name: 'test'}, {tag_count: 1, tag_name: 'test2'}];
        return expectSaga(getAllTagsWorker)
          .provide([
            [matchers.call.fn(metadataAllTags), mockTags],
          ])
          .put({
            type: GetAllTags.SUCCESS,
            payload: { tags: mockTags }
          })
          .run();
      });

      it('handles request error', () => {
        return expectSaga(getAllTagsWorker)
          .provide([
            [matchers.call.fn(metadataAllTags), throwError(new Error())],
          ])
          .put({
            type: GetAllTags.FAILURE,
            payload: { tags: [] }
          })
          .run();
      });
    });
  });
});
