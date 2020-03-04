import { testSaga } from 'redux-saga-test-plan';
import { debounce } from 'redux-saga/effects';

import { DEFAULT_RESOURCE_TYPE, ResourceType, SearchType } from 'interfaces';

import * as NavigationUtils from 'utils/navigationUtils';
import * as SearchUtils from 'ducks/search/utils';

import * as API from '../api/v0';
import * as Utils from '../utils';
import * as Sagas from '../sagas';

import * as filterReducer from '../filters/reducer';
const MOCK_FILTER_STATE = {
  [ResourceType.table]: {
    'database': { 'hive': true }
  }
};
const filterReducerSpy = jest.spyOn(filterReducer, 'default').mockImplementation(() => MOCK_FILTER_STATE);

import reducer, {
  clearSearch,
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
  ClearSearch,
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

import globalState from 'fixtures/globalState';

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
          last_updated_timestamp: 946684799,
          name: 'testName',
          schema: 'testSchema',
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
          last_updated_timestamp: 946684799,
          name: 'testName',
          schema: 'testSchema',
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
    it('searchAll - returns the action to search all resources without useFilters', () => {
      const term = 'test';
      const resource = ResourceType.table;
      const pageIndex = 0;
      const searchType = SearchType.SUBMIT_TERM;
      const action = searchAll(searchType, term, resource, pageIndex);
      const { payload } = action;
      expect(action.type).toBe(SearchAll.REQUEST);
      expect(payload.resource).toBe(resource);
      expect(payload.term).toBe(term);
      expect(payload.pageIndex).toBe(pageIndex);
      expect(payload.useFilters).toBe(false);
      expect(payload.searchType).toBe(searchType);
    });

    it('searchAll - returns the action to search all resources with useFilters', () => {
      const term = 'test';
      const resource = ResourceType.table;
      const pageIndex = 0;
      const searchType = SearchType.SUBMIT_TERM;
      const action = searchAll(searchType, term, resource, pageIndex, true);
      const { payload } = action;
      expect(action.type).toBe(SearchAll.REQUEST);
      expect(payload.resource).toBe(resource);
      expect(payload.term).toBe(term);
      expect(payload.pageIndex).toBe(pageIndex);
      expect(payload.useFilters).toBe(true);
      expect(payload.searchType).toBe(searchType);
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
      const searchType = SearchType.SUBMIT_TERM;
      const action = searchResource(searchType, term, resource, pageIndex);
      const { payload } = action;
      expect(action.type).toBe(SearchResource.REQUEST);
      expect(payload.resource).toBe(resource);
      expect(payload.term).toBe(term);
      expect(payload.pageIndex).toBe(pageIndex);
      expect(payload.searchType).toBe(searchType);
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

    it('submitSearch - returns the action to submit a search without useFilters', () => {
      const term = 'test';
      const action = submitSearch(term);
      expect(action.type).toBe(SubmitSearch.REQUEST);
      expect(action.payload.searchTerm).toBe(term);
      expect(action.payload.useFilters).toBe(false);
    });

    it('submitSearch - returns the action to submit a search with useFilters', () => {
      const term = 'test';
      const action = submitSearch(term, true);
      expect(action.type).toBe(SubmitSearch.REQUEST);
      expect(action.payload.searchTerm).toBe(term);
      expect(action.payload.useFilters).toBe(true);
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

    it('clearSearch - returns the action that will clear the search term', () => {
      const action = clearSearch();
      expect(action.type).toBe(ClearSearch.REQUEST);
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
      expect(reducer(testState, searchAll(SearchType.SUBMIT_TERM, term, ResourceType.table, 0))).toEqual({
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
        filters: testState.filters,
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
      expect(reducer(testState, searchResource(SearchType.SUBMIT_TERM, 'test', ResourceType.table, 0))).toEqual({
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
        filters: filterReducer.initialFilterState,
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

    describe('handles cases that update the filter state', () => {
      describe('cases that update the filter state only', () => {
        it('UpdateSearchFilter.CLEAR_ALL', () => {
          filterReducerSpy.mockClear();
          const filterAction = filterReducer.clearAllFilters();
          const result = reducer(testState, filterAction)
          expect(filterReducerSpy).toHaveBeenCalledWith(testState.filters, filterAction, testState.selectedTab);
          expect(result.filters).toBe(MOCK_FILTER_STATE);
        })
      });

      describe('cases that update the search term & filter state', () => {
        it('UpdateSearchFilter.SET_BY_RESOURCE', () => {
          filterReducerSpy.mockClear();
          const mockTerm = 'rides';
          const filterAction = filterReducer.setSearchInputByResource({ 'tag': 'tagName' }, ResourceType.table, 2, mockTerm);
          const result = reducer(testState, filterAction)
          expect(filterReducerSpy).toHaveBeenCalledWith(testState.filters, filterAction, testState.selectedTab);
          expect(result.filters).toBe(MOCK_FILTER_STATE);
          expect(result.search_term).toBe(mockTerm);
        })
      });

      describe('cases that update the filter state & trigger a search', () => {
        it('UpdateSearchFilter.CLEAR_CATEGORY', () => {
          filterReducerSpy.mockClear();
          const filterAction = filterReducer.clearFilterByCategory('column');
          const result = reducer(testState, filterAction)
          expect(filterReducerSpy).toHaveBeenCalledWith(testState.filters, filterAction, testState.selectedTab);
          expect(result.filters).toBe(MOCK_FILTER_STATE);
          expect(result.isLoading).toBe(true);
        })

        it('UpdateSearchFilter.UPDATE_CATEGORY', () => {
          filterReducerSpy.mockClear();
          const filterAction = filterReducer.updateFilterByCategory('column', 'column_name')
          const result = reducer(testState, filterAction)
          expect(filterReducerSpy).toHaveBeenCalledWith(testState.filters, filterAction, testState.selectedTab);
          expect(result.filters).toBe(MOCK_FILTER_STATE);
          expect(result.isLoading).toBe(true);
        })
      })
    });
  });

  describe('sagas', () => {
    describe('filter sagas', () => {
      describe('filterWatcher', () => {
        it('debounces clear and update category actions with filterWorker', () => {
          testSaga(Sagas.filterWatcher)
            .next()
            .is(debounce(
              750,
              [filterReducer.UpdateSearchFilter.CLEAR_CATEGORY, filterReducer.UpdateSearchFilter.UPDATE_CATEGORY],
              Sagas.filterWorker
            ))
            .next().isDone();
        });
      });

      describe('filterWorker', () => {
        let mockIndex;
        let getPageIndexSpy;
        let mockSearchState;
        let saga;
        beforeAll(() => {
          mockIndex = 1;
          getPageIndexSpy = jest.spyOn(Utils, 'getPageIndex').mockImplementationOnce(() => mockIndex);
          mockSearchState = globalState.search;
          saga = testSaga(Sagas.filterWorker);
        })
        it('verifies saga executes as written', () => {
          /*
            Note: This is an experimental pattern for best effort coverage.
            Sagas have become a mix of both asynchronous api calls & synchronous helper methods --
            unsure if that's a good practice or what it means for writing robust unit tests
          */
          updateSearchUrlSpy.mockClear();
          saga = saga.next().select(SearchUtils.getSearchState).next(mockSearchState);
          expect(getPageIndexSpy).toHaveBeenCalledWith(mockSearchState);
          saga = saga.put(searchResource(SearchType.FILTER, mockSearchState.search_term, mockSearchState.selectedTab, mockIndex)).next();
          expect(updateSearchUrlSpy).toHaveBeenCalledWith({
            filters: mockSearchState.filters,
            resource: mockSearchState.selectedTab,
            term: mockSearchState.search_term,
            index: mockIndex,
          }, true);
          saga.isDone();
        });
      });
    });

    describe('searchAllWatcher', () => {
      it('takes every SearchAll.REQUEST with searchAllWorker', () => {
        testSaga(Sagas.searchAllWatcher)
          .next().takeEvery(SearchAll.REQUEST, Sagas.searchAllWorker)
          .next().isDone();
      });
    });

    describe('searchAllWorker', () => {
      /*
        TODO - There seems to be no straughtforward way to test this method.
        We should re-evaluate how much logic is wrapped into sagas specifically
        question:
        1. Processing the response in the saga
        2. Helper methods
        Can we pass all necessary information to the api method such that the api method
        does all of the processing and returns what we need?
      */

      it('handles request error', () => {
        testSaga(Sagas.searchAllWorker, searchAll(SearchType.SUBMIT_TERM, 'test', ResourceType.table, 0, true))
          .next().select(SearchUtils.getSearchState)
          .next(globalState.search).throw(new Error()).put(searchAllFailure())
          .next().isDone();
      });
    });

    describe('searchResourceWatcher', () => {
      it('takes every SearchResource.REQUEST with searchResourceWorker', () => {
        testSaga(Sagas.searchResourceWatcher)
          .next().takeEvery(SearchResource.REQUEST, Sagas.searchResourceWorker)
          .next().isDone();
      });
    });

    describe('searchResourceWorker', () => {
      it('executes flow for returning search results', () => {
        const pageIndex = 0;
        const resource = ResourceType.table;
        const term = 'test';
        const mockSearchState = globalState.search;
        const searchType = SearchType.PAGINATION;
        testSaga(Sagas.searchResourceWorker, searchResource(searchType, term, resource, pageIndex))
          .next().select(SearchUtils.getSearchState)
          .next(mockSearchState).call(API.searchResource, pageIndex, resource, term, mockSearchState.filters[resource], searchType)
          .next(expectedSearchResults).put(searchResourceSuccess(expectedSearchResults))
          .next().isDone();
      });

      it('handles request error', () => {
        testSaga(Sagas.searchResourceWorker, searchResource(SearchType.PAGINATION, 'test', ResourceType.table, 0))
          .next().select(SearchUtils.getSearchState)
          .next(globalState.search).throw(new Error()).put(searchResourceFailure())
          .next().isDone();
      });
    });

    describe('submitSearchWorker', () => {
      it('initiates a searchAll action', () => {
        const term = 'test';
        const mockSearchState = globalState.search;
        updateSearchUrlSpy.mockClear();
        testSaga(Sagas.submitSearchWorker, submitSearch(term, true))
          .next().select(SearchUtils.getSearchState)
          .next(mockSearchState).put(searchAll(SearchType.SUBMIT_TERM, term, undefined, undefined, true))
          .next().isDone();
          expect(updateSearchUrlSpy).toHaveBeenCalledWith({ term, filters: mockSearchState.filters });

      });
    });

    describe('submitSearchWatcher', () => {
      it('takes every SubmitSearch.REQUEST with submitSearchWorker', () => {
        testSaga(Sagas.submitSearchWatcher)
          .next().takeEvery(SubmitSearch.REQUEST, Sagas.submitSearchWorker)
          .next().isDone();
      });
    });

    describe('setResourceWorker', () => {
      it('calls updateSearchUrl when updateUrl is true', () => {
        const resource = ResourceType.table;
        const updateUrl = true;
        updateSearchUrlSpy.mockClear();
        testSaga(Sagas.setResourceWorker, setResource(resource, updateUrl))
          .next().select(SearchUtils.getSearchState)
          .next(globalState.search).isDone();
        expect(updateSearchUrlSpy).toHaveBeenCalledWith({
          resource,
          term: searchState.search_term,
          index: searchState.tables.page_index,
          filters: searchState.filters,
        });
      });

      it('calls updateSearchUrl when updateUrl is true', () => {
        const resource = ResourceType.table;
        const updateUrl = false;
        updateSearchUrlSpy.mockClear();

        testSaga(Sagas.setResourceWorker, setResource(resource, updateUrl))
          .next().select(SearchUtils.getSearchState)
          .next(searchState).isDone();
        expect(updateSearchUrlSpy).not.toHaveBeenCalled();
      });
    });

    describe('setResourceWatcher', () => {
      it('takes every SetResource.REQUEST with setResourceWorker', () => {
        testSaga(Sagas.setResourceWatcher)
          .next().takeEvery(SetResource.REQUEST, Sagas.setResourceWorker)
          .next().isDone();
      });
    });

    describe('setPageIndexWorker', () => {
      it('initiates a searchResource and updates the url search when specified', () => {
        const index = 1;
        const updateUrl = true;
        updateSearchUrlSpy.mockClear();

        testSaga(Sagas.setPageIndexWorker, setPageIndex(index, updateUrl))
          .next().select(SearchUtils.getSearchState)
          .next(searchState).put(searchResource(SearchType.PAGINATION, searchState.search_term, searchState.selectedTab, index))
          .next().isDone();
        expect(updateSearchUrlSpy).toHaveBeenCalled();
      });

      it('initiates a searchResource and does not update url search', () => {
        const index = 3;
        const updateUrl = false;
        updateSearchUrlSpy.mockClear();

        testSaga(Sagas.setPageIndexWorker, setPageIndex(index, updateUrl))
          .next().select(SearchUtils.getSearchState)
          .next(searchState).put(searchResource(SearchType.PAGINATION, searchState.search_term, searchState.selectedTab, index))
          .next().isDone();
        expect(updateSearchUrlSpy).not.toHaveBeenCalled();
      });
    });

    describe('setPageIndexWatcher', () => {
      it('takes every SetPageIndex.REQUEST with setPageIndexWorker', () => {
        testSaga(Sagas.setPageIndexWatcher)
          .next().takeEvery(SetPageIndex.REQUEST, Sagas.setPageIndexWorker)
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
          return testSaga(Sagas.urlDidUpdateWorker, action)
            .next().select(SearchUtils.getSearchState)
            .next(searchState);
        };
      });

      it('Calls searchAll when search term changes', () => {
        term = 'new search';
        sagaTest(urlDidUpdate(`term=${term}&resource=${resource}&index=${index}`))
          .put(searchAll(SearchType.LOAD_URL, term, resource, index))
          .next().isDone();
      });

      it('Calls setResource when the resource has changed', () => {
        resource = ResourceType.user;
        sagaTest(urlDidUpdate(`term=${term}&resource=${resource}&index=${index}`))
          .put(setResource(resource, false))
          .next().isDone();
      });

      it('when filters have changed', () => {
        sagaTest(urlDidUpdate(`term=${term}&resource=${resource}&index=${index}&filters=%7B"database"%3A%7B"hive"%3Atrue%7D%7D`))
          .put(filterReducer.setSearchInputByResource({ 'database': { 'hive' : true }}, resource, index, term))
          .next().isDone();
      });

      /*it('Calls setPageIndex when the index changes', () => {
        index = 10;
        sagaTest(urlDidUpdate(`term=${term}&resource=${resource}&index=${index}`))
          .put(setPageIndex(index, false))
          .next().isDone();
      });*/
    });

    describe('urlDidUpdateWatcher', () => {
      it('takes every UrlDidUpdate.REQUEST with urlDidUpdateWorker', () => {
        testSaga(Sagas.urlDidUpdateWatcher)
          .next().takeEvery(UrlDidUpdate.REQUEST, Sagas.urlDidUpdateWorker)
          .next().isDone();
      });
    });

    describe('loadPreviousSearchWorker', () => {
      // TODO - test 'BrowserHistory.goBack' case

      it('applies the existing search state into the URL', () => {
        updateSearchUrlSpy.mockClear();

        testSaga(Sagas.loadPreviousSearchWorker, loadPreviousSearch())
          .next().select(SearchUtils.getSearchState)
          .next(searchState).isDone();

        expect(updateSearchUrlSpy).toHaveBeenCalledWith({
          term: searchState.search_term,
          resource: searchState.selectedTab,
          index: SearchUtils.getPageIndex(searchState, searchState.selectedTab),
          filters: searchState.filters,
        });
      });
    });

    describe('loadPreviousSearchWatcher', () => {
      it('takes every LoadPreviousSearch.REQUEST with loadPreviousSearchWorker', () => {
        testSaga(Sagas.loadPreviousSearchWatcher)
          .next().takeEvery(LoadPreviousSearch.REQUEST, Sagas.loadPreviousSearchWorker)
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
        testSaga(Sagas.selectInlineResultsWatcher)
          .next().takeEvery(InlineSearch.SELECT, Sagas.selectInlineResultWorker)
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
