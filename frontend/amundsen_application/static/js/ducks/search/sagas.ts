import { SagaIterator } from 'redux-saga';
import { all, call, debounce, put, select, takeEvery, takeLatest } from 'redux-saga/effects';
import * as _ from 'lodash';
import * as qs from 'simple-query-string';

import { ResourceType, SearchType } from 'interfaces';

import * as API from './api/v0';

import {
  ClearSearch,
  ClearSearchRequest,
  LoadPreviousSearch,
  LoadPreviousSearchRequest,
  SearchAll,
  SearchAllRequest,
  SearchResource,
  SearchResourceRequest,
  InlineSearch,
  InlineSearchRequest,
  SetPageIndex,
  SetPageIndexRequest, SetResource, SetResourceRequest,
  SubmitSearch,
  SubmitSearchRequest,
  UrlDidUpdate,
  UrlDidUpdateRequest,
} from './types';

import {
  initialState,
  initialInlineResultsState,
  searchAll,
  searchAllFailure,
  searchAllSuccess,
  searchResource,
  searchResourceFailure,
  searchResourceSuccess,
  getInlineResults,
  getInlineResultsDebounce,
  getInlineResultsSuccess,
  getInlineResultsFailure,
  updateFromInlineResult,
  setPageIndex, setResource,
} from './reducer';
import {
  clearAllFilters,
  setSearchInputByResource,
  UpdateSearchFilter
} from './filters/reducer';
import { autoSelectResource, getPageIndex, getSearchState } from './utils';
import { BrowserHistory, updateSearchUrl } from 'utils/navigationUtils';

/**
 * Listens to actions triggers by user updates to the filter state.
 * For better user experience debounce the start of the worker as multiple updates can happen in < 1 second.
 */
export function* filterWatcher(): SagaIterator {
  yield debounce(750, [UpdateSearchFilter.CLEAR_CATEGORY, UpdateSearchFilter.UPDATE_CATEGORY], filterWorker);
};

/*
 * Executes a search on the current resource.
 * Actions that trigger this worker will have updated the filter reducer.
 * The updated filter state is applied in searchResourceWorker().
 * Updates the search url to reflect the change in filters.
 */
export function* filterWorker(): SagaIterator {
  const state = yield select(getSearchState);
  const { search_term, selectedTab, filters } = state;
  /* filters must reset pageIndex to 0 as the number of results is expected to change */
  const pageIndex = 0;
  yield put(searchResource(SearchType.FILTER, search_term, selectedTab, pageIndex));
  updateSearchUrl({ filters, resource: selectedTab, term: search_term, index: pageIndex }, true);
};

/**
 * Listens to actions triggers by application updates to both the filter state and search term.
 * This is intended to be temporary code. searchResource saga restructring will allow us to consolidate this support.
 */
export function* filterWatcher2(): SagaIterator {
  yield takeLatest(UpdateSearchFilter.SET_BY_RESOURCE, filterWorker2);
};

/**
 * Executes a search on the given resource.
 * Actions that trigger this worker will have updated the filter reducer.
 * The updated filter state is applied in searchResourceWorker().
 * Updates the search url to reflect the change in filters.
 * This is intended to be temporary code. searchResource Saga restructring will allow us to consolidate this support.
 */
export function* filterWorker2(action: any): SagaIterator {
  const state = yield select(getSearchState);
  const { pageIndex = 0, resourceType, term = '' } = action.payload;
  yield put(searchResource(SearchType.FILTER, term, resourceType, pageIndex));
  updateSearchUrl({ term, filters: state.filters, resource: resourceType, index: pageIndex }, false);
};

export function* inlineSearchWorker(action: InlineSearchRequest): SagaIterator {
  const { term } = action.payload;
  try {
    const [tableResponse, userResponse] = yield all([
      call(API.searchResource, 0, ResourceType.table, term, {}, SearchType.INLINE_SEARCH),
      call(API.searchResource, 0, ResourceType.user, term, {}, SearchType.INLINE_SEARCH),
    ]);
    const inlineSearchResponse = {
      tables: tableResponse.tables || initialInlineResultsState.tables,
      users: userResponse.users || initialInlineResultsState.users,
    };
    yield put(getInlineResultsSuccess(inlineSearchResponse));
  } catch (e) {
    yield put(getInlineResultsFailure());
  }
};
export function* inlineSearchWatcher(): SagaIterator {
  yield takeLatest(InlineSearch.REQUEST, inlineSearchWorker);
}
export function* debounceWorker(action): SagaIterator {
  yield put(getInlineResults(action.payload.term));
}
export function* inlineSearchWatcherDebounce(): SagaIterator {
  yield debounce(350, InlineSearch.REQUEST_DEBOUNCE, debounceWorker);
}

export function* selectInlineResultWorker(action): SagaIterator {
  const state = yield select();
  const { searchTerm, resourceType, updateUrl } = action.payload;
  if (state.search.inlineResults.isLoading) {
    yield put(searchAll(SearchType.INLINE_SELECT, searchTerm, resourceType, 0, false))
    updateSearchUrl({ term: searchTerm, filters: state.search.filters });
  }
  else {
    if (updateUrl) {
      updateSearchUrl({ resource: resourceType, term: searchTerm, index: 0, filters: state.search.filters });
    }
    const data = {
      searchTerm,
      selectedTab: resourceType,
      tables: state.search.inlineResults.tables,
      users: state.search.inlineResults.users,
    };
    yield put(updateFromInlineResult(data));
  }
};
export function* selectInlineResultsWatcher(): SagaIterator {
  yield takeEvery(InlineSearch.SELECT, selectInlineResultWorker);
};

export function* submitSearchWorker(action: SubmitSearchRequest): SagaIterator {
  const state = yield select(getSearchState);
  const { searchTerm, useFilters } = action.payload;
  yield put(searchAll(SearchType.SUBMIT_TERM, searchTerm, undefined, undefined, useFilters));
  updateSearchUrl({ term: searchTerm, filters: state.filters });
};
export function* submitSearchWatcher(): SagaIterator {
  yield takeEvery(SubmitSearch.REQUEST, submitSearchWorker);
};

export function* setResourceWorker(action: SetResourceRequest): SagaIterator {
  const { resource, updateUrl } = action.payload;
  const state = yield select(getSearchState);
  if (updateUrl) {
    updateSearchUrl({
      resource,
      term: state.search_term,
      index: getPageIndex(state, resource),
      filters: state.filters,
    });
  }
};
export function* setResourceWatcher(): SagaIterator {
  yield takeEvery(SetResource.REQUEST, setResourceWorker);
};

export function* setPageIndexWorker(action: SetPageIndexRequest): SagaIterator {
  const { pageIndex, updateUrl } = action.payload;
  const state = yield select(getSearchState);
  yield put(searchResource(SearchType.PAGINATION, state.search_term, state.selectedTab, pageIndex));

  if (updateUrl) {
    updateSearchUrl({
      term: state.search_term,
      resource: state.selectedTab,
      index: pageIndex,
      filters: state.filters,
    });
  }
};
export function* setPageIndexWatcher(): SagaIterator {
  yield takeEvery(SetPageIndex.REQUEST, setPageIndexWorker);
};

export function* clearSearchWorker(action: ClearSearchRequest): SagaIterator {
  /* If there was a previous search term, search each resource using filters */
  const state = yield select(getSearchState);
  if (!!state.search_term) {
    yield put(searchAll(SearchType.CLEAR_TERM, '', undefined, undefined, true));
  }
};
export function* clearSearchWatcher(): SagaIterator {
  yield takeEvery(ClearSearch.REQUEST, clearSearchWorker);
};

export function* urlDidUpdateWorker(action: UrlDidUpdateRequest): SagaIterator {
  const { urlSearch } = action.payload;
  const { term = '', resource, index, filters } = qs.parse(urlSearch);
  const parsedIndex = parseInt(index, 10);
  const parsedFilters = filters ? JSON.parse(filters) : null;

  const state = yield select(getSearchState);
  if (!!term && state.search_term !== term) {
    yield put(searchAll(SearchType.LOAD_URL, term, resource, parsedIndex));
  } else if (!!resource) {
    if (resource !== state.selectedTab) {
      yield put(setResource(resource, false))
    }
    if (parsedFilters && !_.isEqual(state.filters[resource], parsedFilters)) {
      /* This will update filter state + search resource */
      yield put(setSearchInputByResource(parsedFilters, resource, parsedIndex, term));
    }
  } else if (!isNaN(parsedIndex) && parsedIndex !== getPageIndex(state, resource)) {
    /*
     Note: Current filtering logic seems to reproduction of this case.
     Could there be a race condition between url and reducer state updates?
     Re-evaluate when restrucuring sagas to consolidate filter support.
    */
    yield put(setPageIndex(parsedIndex, false));
  }
};
export function* urlDidUpdateWatcher(): SagaIterator {
  yield takeEvery(UrlDidUpdate.REQUEST, urlDidUpdateWorker);
};

export function* loadPreviousSearchWorker(action: LoadPreviousSearchRequest): SagaIterator {
  const state = yield select(getSearchState);
  if (state.search_term === "") {
    BrowserHistory.goBack();
    return;
  }
  updateSearchUrl({
    term: state.search_term,
    resource: state.selectedTab,
    index: getPageIndex(state),
    filters: state.filters,
  });
};
export function* loadPreviousSearchWatcher(): SagaIterator {
  yield takeEvery(LoadPreviousSearch.REQUEST, loadPreviousSearchWorker);
};

//////////////////////////////////////////////////////////////////////////////
//  API/END SAGAS
//  These sagas directly trigger axios search requests.
//  The actions that trigger them should only be fired by other sagas,
//  and these sagas should be considered the "end" of any saga chain.
//////////////////////////////////////////////////////////////////////////////

export function* searchResourceWorker(action: SearchResourceRequest): SagaIterator {
  const { pageIndex, resource, term, searchType } = action.payload;
  const state = yield select(getSearchState);
  try {
    const searchResults = yield call(API.searchResource, pageIndex, resource, term, state.filters[resource], searchType);
    yield put(searchResourceSuccess(searchResults));
  } catch (e) {
    yield put(searchResourceFailure());
  }
};
export function* searchResourceWatcher(): SagaIterator {
  yield takeEvery(SearchResource.REQUEST, searchResourceWorker);
};

export function* searchAllWorker(action: SearchAllRequest): SagaIterator {
  let { resource } = action.payload;
  const { pageIndex, term, useFilters, searchType } = action.payload;
  if (!useFilters) {
    yield put(clearAllFilters())
  }

  const state = yield select(getSearchState);
  const tableIndex = resource === ResourceType.table ? pageIndex : 0;
  const userIndex = resource === ResourceType.user ? pageIndex : 0;
  const dashboardIndex = resource === ResourceType.dashboard ? pageIndex : 0;

  try {
    const [tableResponse, userResponse, dashboardResponse] = yield all([
      call(API.searchResource, tableIndex, ResourceType.table, term, state.filters[ResourceType.table], searchType),
      call(API.searchResource, userIndex, ResourceType.user, term, state.filters[ResourceType.user], searchType),
      call(API.searchResource, dashboardIndex, ResourceType.dashboard, term, state.filters[ResourceType.dashboard], searchType),
    ]);
    const searchAllResponse = {
      search_term: term,
      selectedTab: resource,
      tables: tableResponse.tables || initialState.tables,
      users: userResponse.users || initialState.users,
      dashboards: dashboardResponse.dashboards || initialState.dashboards,
      isLoading: false,
    };
    if (resource === undefined) {
      resource = autoSelectResource(searchAllResponse);
      searchAllResponse.selectedTab = resource;
    }
    const index = getPageIndex(searchAllResponse);
    yield put(searchAllSuccess(searchAllResponse));
    updateSearchUrl({ term, resource, index, filters: state.filters }, true);

  } catch (e) {
    yield put(searchAllFailure());
  }
};
export function* searchAllWatcher(): SagaIterator {
  yield takeEvery(SearchAll.REQUEST, searchAllWorker);
};
