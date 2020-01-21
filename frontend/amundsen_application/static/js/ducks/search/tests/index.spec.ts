import { testSaga } from 'redux-saga-test-plan';

import { DEFAULT_RESOURCE_TYPE, ResourceType } from 'interfaces';

import * as API from '../api/v0';

import reducer, {
  getInlineResults,
  getInlineResultsSuccess,
  getInlineResultsFailure,
  initialState,
  initialInlineResultsState,
  loadPreviousSearch,
  searchAll,
  searchAllFailure,
  searchAllSuccess,
  SearchReducerState,
  searchReset,
  searchResource,
  searchResourceFailure,
  searchResourceSuccess,
  selectInlineResult,
  setPageIndex,
  setResource,
  submitSearch,
  updateFromInlineResult,
  urlDidUpdate,
} from '../reducer';
import {
  inlineSearchWatcher,
  inlineSearchWorker,
  loadPreviousSearchWatcher,
  loadPreviousSearchWorker,
  searchAllWatcher,
  searchAllWorker,
  searchResourceWatcher,
  searchResourceWorker,
  selectInlineResultsWatcher,
  selectInlineResultWorker,
  setPageIndexWatcher,
  setPageIndexWorker,
  setResourceWatcher,
  setResourceWorker,
  submitSearchWatcher,
  submitSearchWorker,
  urlDidUpdateWatcher,
  urlDidUpdateWorker
} from '../sagas';
import {
  LoadPreviousSearch,
  InlineSearch,
  InlineSearchResponsePayload,
  InlineSearchUpdatePayload,
  SearchAll,
  SearchAllResponsePayload,
  SearchResource,
  SearchResponsePayload,
  SetPageIndex,
  SetResource,
  SubmitSearch,
  UrlDidUpdate,
} from '../types';
import * as NavigationUtils from '../../../utils/navigation-utils';
import * as SearchUtils from 'ducks/search/utils';

import globalState from '../../../fixtures/globalState';

const updateSearchUrlSpy = jest.spyOn(NavigationUtils, 'updateSearchUrl');
const searchState = globalState.search;

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

  const expectedInlineResults: InlineSearchResponsePayload = {
    tables: {
      page_index: 0,
      results: [],
      total_results: 0,
    },
    users: {
      page_index: 0,
      results: [],
      total_results: 0,
    }
  };

  const inlineUpdatePayload: InlineSearchUpdatePayload = {
    searchTerm: 'testName',
    selectedTab: ResourceType.table,
    tables: {
      page_index: 0,
      results: [],
      total_results: 0,
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

    it('submitSearch - returns the action to submit a search', () => {
      const term = 'test';
      const action = submitSearch(term);
      expect(action.type).toBe(SubmitSearch.REQUEST);
      expect(action.payload.searchTerm).toBe(term);
    });

    it('setResource - returns the action to set the selected resource', () => {
      const resource = ResourceType.table;
      const updateUrl = true;
      const action = setResource(resource, updateUrl);
      const { payload } = action;
      expect(action.type).toBe(SetResource.REQUEST);
      expect(payload.resource).toBe(resource);
      expect(payload.updateUrl).toBe(updateUrl);
    });

    it('setPageIndex - returns the action to set the page index', () => {
      const index = 3;
      const updateUrl = true;
      const action = setPageIndex(index, updateUrl);
      const { payload } = action;
      expect(action.type).toBe(SetPageIndex.REQUEST);
      expect(payload.pageIndex).toBe(index);
      expect(payload.updateUrl).toBe(updateUrl);
    });

    it('loadPreviousSearch - returns the action to load the previous search', () => {
      const action = loadPreviousSearch();
      expect(action.type).toBe(LoadPreviousSearch.REQUEST);
    });

    it('urlDidUpdate - returns the action to run when the search page URL changes', () => {
      const urlSearch = 'test url search';
      const action = urlDidUpdate(urlSearch);
      expect(action.type).toBe(UrlDidUpdate.REQUEST);
      expect(action.payload.urlSearch).toBe(urlSearch);
    });

    it('getInlineResultsSuccess - returns the action to get inline results', () => {
      const term = 'test'
      const action = getInlineResults(term);
      expect(action.type).toBe(InlineSearch.REQUEST);
      expect(action.payload.term).toBe(term);
    });

    it('getInlineResultsSuccess - returns the action to process the success', () => {
      const action = getInlineResultsSuccess(expectedInlineResults);
      const { payload } = action;
      expect(action.type).toBe(InlineSearch.SUCCESS);
      expect(payload).toBe(expectedInlineResults);
    });

    it('getInlineResultsFailure - returns the action to process the failure', () => {
      const action = getInlineResultsFailure();
      expect(action.type).toBe(InlineSearch.FAILURE);
    });

    it('selectInlineResult - returns the action to process the selection of an inline result', () => {
      const resource = ResourceType.table;
      const searchTerm = 'test;'
      const updateUrl = true;
      const action = selectInlineResult(resource, searchTerm, updateUrl);
      const { payload } = action;
      expect(action.type).toBe(InlineSearch.SELECT);
      expect(payload.resourceType).toBe(resource);
      expect(payload.searchTerm).toBe(searchTerm);
      expect(payload.updateUrl).toBe(updateUrl);
    });

    it('updateFromInlineResult - returns the action to populate the search results with existing inlineResults', () => {
      const action = updateFromInlineResult(inlineUpdatePayload)
      expect(action.type).toBe(InlineSearch.UPDATE);
      expect(action.payload).toBe(inlineUpdatePayload);
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
        inlineResults: initialInlineResultsState,
        search_term: term,
        isLoading: true,
      });
    });

    it('should handle SearchAll.SUCCESS', () => {
      expect(reducer(testState, searchAllSuccess(expectedSearchAllResults))).toEqual({
        ...initialState,
        ...expectedSearchAllResults,
        inlineResults: {
          tables: expectedSearchAllResults.tables,
          users: expectedSearchAllResults.users,
          isLoading: false,
        },
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

    it('should handle SetResource.REQUEST', () => {
      const selectedTab = ResourceType.user;
      expect(reducer(testState, setResource(selectedTab))).toEqual({
        ...testState,
        selectedTab,
      });
    });

    it('should handle InlineSearch.UPDATE', () => {
      const { searchTerm, selectedTab, tables, users } = inlineUpdatePayload;
      expect(reducer(testState, updateFromInlineResult(inlineUpdatePayload))).toEqual({
        ...testState,
        selectedTab,
        tables,
        users,
        search_term: searchTerm,
      });
    });

    it('should handle InlineSearch.SUCCESS', () => {
      const { tables, users } = expectedInlineResults;
      expect(reducer(testState, getInlineResultsSuccess(expectedInlineResults))).toEqual({
        ...testState,
        inlineResults: {
          tables,
          users,
          isLoading: false,
        }
      });
    });

    it('should handle InlineSearch.FAILURE', () => {
      expect(reducer(testState, getInlineResultsFailure())).toEqual({
        ...testState,
        inlineResults: initialInlineResultsState,
      });
    });

    it('should handle InlineSearch.REQUEST', () => {
      const term = 'testSearch';
      expect(reducer(testState, getInlineResults(term))).toEqual({
        ...testState,
        inlineResults: {
          tables: initialInlineResultsState.tables,
          users: initialInlineResultsState.users,
          isLoading: true,
        },
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

    describe('submitSearchWorker', () => {
      it('initiates a searchAll action', () => {
        const term = 'test';
        updateSearchUrlSpy.mockClear();
        testSaga(submitSearchWorker, submitSearch(term))
          .next().put(searchAll(term))
          .next().isDone();
          expect(updateSearchUrlSpy).toHaveBeenCalledWith({ term });

      });
    });

    describe('submitSearchWatcher', () => {
      it('takes every SubmitSearch.REQUEST with submitSearchWorker', () => {
        testSaga(submitSearchWatcher)
          .next().takeEvery(SubmitSearch.REQUEST, submitSearchWorker)
          .next().isDone();
      });
    });

    describe('setResourceWorker', () => {
      it('calls updateSearchUrl when updateUrl is true', () => {
        const resource = ResourceType.table;
        const updateUrl = true;
        updateSearchUrlSpy.mockClear();
        testSaga(setResourceWorker, setResource(resource, updateUrl))
          .next().select(SearchUtils.getSearchState)
          .next(globalState.search).isDone();
        expect(updateSearchUrlSpy).toHaveBeenCalledWith({
          resource,
          term: searchState.search_term,
          index: searchState.tables.page_index,
        });
      });

      it('calls updateSearchUrl when updateUrl is true', () => {
        const resource = ResourceType.table;
        const updateUrl = false;
        updateSearchUrlSpy.mockClear();

        testSaga(setResourceWorker, setResource(resource, updateUrl))
          .next().select(SearchUtils.getSearchState)
          .next(searchState).isDone();
        expect(updateSearchUrlSpy).not.toHaveBeenCalled();
      });
    });

    describe('setResourceWatcher', () => {
      it('takes every SetResource.REQUEST with setResourceWorker', () => {
        testSaga(setResourceWatcher)
          .next().takeEvery(SetResource.REQUEST, setResourceWorker)
          .next().isDone();
      });
    });

    describe('setPageIndexWorker', () => {
      it('initiates a searchResource and updates the url search when specified', () => {
        const index = 1;
        const updateUrl = true;
        updateSearchUrlSpy.mockClear();

        testSaga(setPageIndexWorker, setPageIndex(index, updateUrl))
          .next().select(SearchUtils.getSearchState)
          .next(searchState).put(searchResource(searchState.search_term, searchState.selectedTab, index))
          .next().isDone();
        expect(updateSearchUrlSpy).toHaveBeenCalled();
      });

      it('initiates a searchResource and does not update url search', () => {
        const index = 3;
        const updateUrl = false;
        updateSearchUrlSpy.mockClear();

        testSaga(setPageIndexWorker, setPageIndex(index, updateUrl))
          .next().select(SearchUtils.getSearchState)
          .next(searchState).put(searchResource(searchState.search_term, searchState.selectedTab, index))
          .next().isDone();
        expect(updateSearchUrlSpy).not.toHaveBeenCalled();
      });
    });

    describe('setPageIndexWatcher', () => {
      it('takes every SetPageIndex.REQUEST with setPageIndexWorker', () => {
        testSaga(setPageIndexWatcher)
          .next().takeEvery(SetPageIndex.REQUEST, setPageIndexWorker)
          .next().isDone();
      });
    });

    describe('urlDidUpdateWorker', () => {
      let sagaTest;
      let term;
      let resource;
      let index;

      beforeEach(() => {
        term = searchState.search_term;
        resource = searchState.selectedTab;
        index = SearchUtils.getPageIndex(searchState, resource);

        sagaTest = (action) => {
          return testSaga(urlDidUpdateWorker, action)
            .next().select(SearchUtils.getSearchState)
            .next(searchState);
        };
      });

      it('Calls searchAll when search term changes', () => {
        term = 'new search';
        sagaTest(urlDidUpdate(`term=${term}&resource=${resource}&index=${index}`))
          .put(searchAll(term, resource, index))
          .next().isDone();
      });

      it('Calls setResource when the resource has changed', () => {
        resource = ResourceType.user;
        sagaTest(urlDidUpdate(`term=${term}&resource=${resource}&index=${index}`))
          .put(setResource(resource, false))
          .next().isDone();
      });

      it('Calls setPageIndex when the index changes', () => {
        index = 10;
        sagaTest(urlDidUpdate(`term=${term}&resource=${resource}&index=${index}`))
          .put(setPageIndex(index, false))
          .next().isDone();
      });
    });

    describe('urlDidUpdateWatcher', () => {
      it('takes every UrlDidUpdate.REQUEST with urlDidUpdateWorker', () => {
        testSaga(urlDidUpdateWatcher)
          .next().takeEvery(UrlDidUpdate.REQUEST, urlDidUpdateWorker)
          .next().isDone();
      });
    });

    describe('loadPreviousSearchWorker', () => {
      // TODO - test 'BrowserHistory.goBack' case

      it('applies the existing search state into the URL', () => {
        updateSearchUrlSpy.mockClear();

        testSaga(loadPreviousSearchWorker, loadPreviousSearch())
          .next().select(SearchUtils.getSearchState)
          .next(searchState).isDone();

        expect(updateSearchUrlSpy).toHaveBeenCalledWith({
          term: searchState.search_term,
          resource: searchState.selectedTab,
          index: SearchUtils.getPageIndex(searchState, searchState.selectedTab),
        });
      });
    });

    describe('loadPreviousSearchWatcher', () => {
      it('takes every LoadPreviousSearch.REQUEST with loadPreviousSearchWorker', () => {
        testSaga(loadPreviousSearchWatcher)
          .next().takeEvery(LoadPreviousSearch.REQUEST, loadPreviousSearchWorker)
          .next().isDone();
      });
    });

    describe('inlineSearchWorker', () => {
      /* TODO - Considering some cleanup */
    });

    describe('inlineSearchWatcher', () => {
      /* TODO - Need to investigate proper test approach
      it('debounces InlineSearch.REQUEST and calls inlineSearchWorker', () => {
      });
      */
    });

    describe('selectInlineResultWorker', () => {
      /* TODO - Considering some cleanup */
    });

    describe('selectInlineResultsWatcher', () => {
      it('takes every InlineSearch.REQUEST with selectInlineResultWorker', () => {
        testSaga(selectInlineResultsWatcher)
          .next().takeEvery(InlineSearch.SELECT, selectInlineResultWorker)
          .next().isDone();
      });
    });
  });

  describe('utils', () => {
    describe('getSearchState', () => {
      it('returns the search state', () => {
        const result = SearchUtils.getSearchState(globalState);
        expect(result).toEqual(searchState);
      });
    });

    describe('getPageIndex', () => {
      const mockState = {
        ...searchState,
        selectedTab: ResourceType.dashboard,
        dashboards: {
          ...searchState.dashboards,
          page_index: 1,
        },
        tables: {
          ...searchState.tables,
          page_index: 2,
        },
        users: {
          ...searchState.users,
          page_index: 3,
        }
      };

      it('given ResourceType.dashboard, returns page_index for dashboards', () => {
        expect(SearchUtils.getPageIndex(mockState, ResourceType.dashboard)).toEqual(mockState.dashboards.page_index);
      });

      it('given ResourceType.table, returns page_index for table', () => {
        expect(SearchUtils.getPageIndex(mockState, ResourceType.table)).toEqual(mockState.tables.page_index);
      });

      it('given ResourceType.user, returns page_index for users', () => {
        expect(SearchUtils.getPageIndex(mockState, ResourceType.user)).toEqual(mockState.users.page_index);
      });

      it('given no resource, returns page_index for the selected resource', () => {
        const resourceToUse = mockState[mockState.selectedTab + 's'];
        expect(SearchUtils.getPageIndex(mockState)).toEqual(resourceToUse.page_index);
      });

      it('returns 0 if not given a supported ResourceType', () => {
        // @ts-ignore: cover default case
        expect(SearchUtils.getPageIndex(mockState, 'not valid input')).toEqual(0);
      });
    });

    describe('autoSelectResource', () => {
      const emptyMockState = {
        ...searchState,
        dashboards: {
          ...searchState.dashboards,
          total_results: 0,
        },
        tables: {
          ...searchState.tables,
          total_results: 0,
        },
        users: {
          ...searchState.users,
          total_results: 0,
        }
      };

      it('returns the DEFAULT_RESOURCE_TYPE when search results are empty', () => {
        expect(SearchUtils.autoSelectResource(emptyMockState)).toEqual(DEFAULT_RESOURCE_TYPE);
      });

      it('prefers `table` over `user` and `dashboard`', () => {
        const mockState = { ...emptyMockState };
        mockState.tables.total_results = 10;
        mockState.users.total_results = 10;
        mockState.dashboards.total_results = 10;
        expect(SearchUtils.autoSelectResource(mockState)).toEqual(ResourceType.table);
      });

      it('prefers `user` over `dashboard`', () => {
        const mockState = { ...emptyMockState };
        mockState.tables.total_results = 0;
        mockState.users.total_results = 10;
        mockState.dashboards.total_results = 10;
        expect(SearchUtils.autoSelectResource(mockState)).toEqual(ResourceType.user);
      });

      it('returns `dashboard` if there are dashboards but no other results', () => {
        const mockState = { ...emptyMockState };
        mockState.tables.total_results = 0;
        mockState.users.total_results = 0;
        mockState.dashboards.total_results = 10;
        expect(SearchUtils.autoSelectResource(mockState)).toEqual(ResourceType.dashboard);
      });
    });
  });
});
