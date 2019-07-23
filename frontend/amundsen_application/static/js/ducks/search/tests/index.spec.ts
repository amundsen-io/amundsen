import { testSaga } from 'redux-saga-test-plan';

import { ResourceType } from 'interfaces';

import * as API from '../api/v0';

import reducer, {
  initialState,
  searchAll,
  searchAllFailure,
  searchAllSuccess,
  SearchReducerState,
  searchReset,
  searchResource,
  searchResourceFailure,
  searchResourceSuccess,
  updateSearchTab,
} from '../reducer';
import { searchAllWatcher, searchAllWorker, searchResourceWatcher, searchResourceWorker } from '../sagas';
import { SearchAll, SearchAllResponsePayload, SearchResource, SearchResponsePayload, UpdateSearchTab, } from '../types';

describe('search ducks', () => {
  const expectedSearchResults: SearchResponsePayload = {
    search_term: 'testName',
    tables: {
      page_index: 0,
      results: [
        {
          cluster: 'testCluster',
          database: 'testDatabase',
          description: 'I have a lot of users',
          key: 'testDatabase://testCluster.testSchema/testName',
          last_updated_epoch: 946684799,
          name: 'testName',
          schema_name: 'testSchema',
          type: ResourceType.table,
        },
      ],
      total_results: 1,
    },
  };
  const expectedSearchAllResults: SearchAllResponsePayload = {
    search_term: 'testName',
    selectedTab: ResourceType.table,
    dashboards: {
      page_index: 0,
      results: [],
      total_results: 0,
    },
    tables: {
      page_index: 0,
      results: [
        {
          cluster: 'testCluster',
          database: 'testDatabase',
          description: 'I have a lot of users',
          key: 'testDatabase://testCluster.testSchema/testName',
          last_updated_epoch: 946684799,
          name: 'testName',
          schema_name: 'testSchema',
          type: ResourceType.table,
        },
      ],
      total_results: 1,
    },
    users: {
      page_index: 0,
      results: [],
      total_results: 0,
    },
  };

  describe('actions', () => {
    it('searchAll - returns the action to search all resources', () => {
      const term = 'test';
      const resource = ResourceType.table;
      const pageIndex = 0;
      const action = searchAll(term, resource, pageIndex);
      const { payload } = action;
      expect(action.type).toBe(SearchAll.REQUEST);
      expect(payload.resource).toBe(resource);
      expect(payload.term).toBe(term);
      expect(payload.pageIndex).toBe(pageIndex);
    });

    it('searchAllSuccess - returns the action to process the success', () => {
      const action = searchAllSuccess(expectedSearchAllResults);
      const { payload } = action;
      expect(action.type).toBe(SearchAll.SUCCESS);
      expect(payload).toBe(expectedSearchAllResults);
    });

    it('searchAllFailure - returns the action to process the failure', () => {
      const action = searchAllFailure();
      expect(action.type).toBe(SearchAll.FAILURE);
    });

    it('searchResource - returns the action to search all resources', () => {
      const term = 'test';
      const resource = ResourceType.table;
      const pageIndex = 0;
      const action = searchResource(term, resource, pageIndex);
      const { payload } = action;
      expect(action.type).toBe(SearchResource.REQUEST);
      expect(payload.resource).toBe(resource);
      expect(payload.term).toBe(term);
      expect(payload.pageIndex).toBe(pageIndex);
    });

    it('searchResourceSuccess - returns the action to process the success', () => {
      const action = searchResourceSuccess(expectedSearchResults);
      const { payload } = action;
      expect(action.type).toBe(SearchResource.SUCCESS);
      expect(payload).toBe(expectedSearchResults);
    });

    it('searchResourceFailure - returns the action to process the failure', () => {
      const action = searchResourceFailure();
      expect(action.type).toBe(SearchResource.FAILURE);
    });

    it('searchReset - returns the action to reset search state', () => {
      const action = searchReset();
      expect(action.type).toBe(SearchAll.RESET);
    });

    it('updateSearchTab - returns the action to update the search tab', () => {
      const selectedTab = ResourceType.user;
      const action = updateSearchTab(selectedTab);
      const payload = action.payload;
      expect(action.type).toBe(UpdateSearchTab.REQUEST);
      expect(payload.selectedTab).toBe(selectedTab);
    });
  });

  describe('reducer', () => {
    let testState: SearchReducerState;
    beforeAll(() => {
      testState = initialState;
    });
    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
    });

    it('should handle SearchAll.REQUEST', () => {
      const term = 'testSearch';
      const resource = ResourceType.table;
      const pageIndex = 0;
      expect(reducer(testState, searchAll(term, resource, pageIndex))).toEqual({
        ...testState,
        search_term: term,
        isLoading: true,
      });
    });

    it('should handle SearchAll.SUCCESS', () => {
      expect(reducer(testState, searchAllSuccess(expectedSearchAllResults))).toEqual({
        ...initialState,
        ...expectedSearchResults,
        isLoading: false,
      });
    });

    it('should handle SearchAll.FAILURE', () => {
      expect(reducer(testState, searchAllFailure())).toEqual({
        ...initialState,
        search_term: testState.search_term,
      });
    });

    it('should handle SearchAll.RESET', () => {
      expect(reducer(testState, searchReset())).toEqual(initialState);
    });

    it('should handle SearchResource.REQUEST', () => {
      expect(reducer(testState, searchResource('test', ResourceType.table, 0))).toEqual({
        ...initialState,
        isLoading: true,
      });
    });

    it('should handle SearchResource.SUCCESS', () => {
      expect(reducer(testState, searchResourceSuccess(expectedSearchResults))).toEqual({
        ...initialState,
        ...expectedSearchResults,
        isLoading: false,
      });
    });

    it('should handle SearchResource.FAILURE', () => {
      expect(reducer(testState, searchResourceFailure())).toEqual({
        ...initialState,
        search_term: testState.search_term,
      });
    });

    it('should handle UpdateSearchTab.REQUEST', () => {
      const selectedTab = ResourceType.user;
      expect(reducer(testState, updateSearchTab(selectedTab))).toEqual({
        ...testState,
        selectedTab,
      });
    });
  });

  describe('sagas', () => {
    describe('searchAllWatcher', () => {
      it('takes every SearchAll.REQUEST with searchAllWorker', () => {
        testSaga(searchAllWatcher)
          .next().takeEvery(SearchAll.REQUEST, searchAllWorker)
          .next().isDone();
      });
    });

    describe('searchAllWorker', () => {
      /* TODO - Improve this test
      it('executes flow for returning search results', () => {
        const term = 'testSearch';
        const options = {};
        testSaga(searchAllWorker, searchAll(term, options))
          .next()
          .call(srchAll, options, term)
          .next(expectedSearchResults)
          .put(searchAllSuccess(expectedSearchResults))
          .next()
          .isDone();
      });*/

      it('handles request error', () => {
        testSaga(searchAllWorker, searchAll('test', ResourceType.table, 0))
          .next().throw(new Error()).put(searchAllFailure())
          .next().isDone();
      });
    });

    describe('searchResourceWatcher', () => {
      it('takes every SearchResource.REQUEST with searchResourceWorker', () => {
        testSaga(searchResourceWatcher)
          .next().takeEvery(SearchResource.REQUEST, searchResourceWorker)
          .next().isDone();
      });
    });

    describe('searchResourceWorker', () => {
      it('executes flow for returning search results', () => {
        const pageIndex = 0;
        const resource = ResourceType.table;
        const term = 'test';
        testSaga(searchResourceWorker, searchResource(term, resource, pageIndex))
          .next().call(API.searchResource, pageIndex, resource, term)
          .next(expectedSearchResults).put(searchResourceSuccess(expectedSearchResults))
          .next().isDone();
      });

      it('handles request error', () => {
        testSaga(searchResourceWorker, searchResource('test', ResourceType.table, 0))
          .next().throw(new Error()).put(searchResourceFailure())
          .next().isDone();
      });
    });
  });
});
