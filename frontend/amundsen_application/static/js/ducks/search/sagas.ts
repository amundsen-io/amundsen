import { SagaIterator } from 'redux-saga';
import {
  call,
  debounce,
  put,
  select,
  takeEvery,
  takeLatest,
} from 'redux-saga/effects';
import * as isEqual from 'lodash/isEqual';
import * as qs from 'simple-query-string';

import { ResourceType, SearchType } from 'interfaces';

import { BrowserHistory, updateSearchUrl } from 'utils/navigationUtils';
import { getSearchResultsPerPage } from 'config/config-utils';
import * as API from './api/v0';

import {
  LoadPreviousSearch,
  SearchAll,
  SearchAllRequest,
  SearchResource,
  SearchResourceRequest,
  InlineSearch,
  InlineSearchRequest,
  SubmitSearch,
  SubmitSearchRequest,
  SubmitSearchResource,
  SubmitSearchResourceRequest,
  UpdateSearchState,
  UpdateSearchStateRequest,
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
  getInlineResultsSuccess,
  getInlineResultsFailure,
  updateFromInlineResult,
  updateSearchState,
  submitSearchResource,
} from './reducer';
import { initialFilterState } from './filters/reducer';
import { autoSelectResource, getPageIndex, getSearchState } from './utils';

//  SEARCH SAGAS
//  The actions that trigger these sagas are fired directly from components.

/**
 * Handles workflow for any user action that causes an update to the searchTerm,
 * which requires that all resources be re-searched.
 */

const SEARCHABLE_RESOURCES = [
  ResourceType.table,
  ResourceType.dashboard,
  ResourceType.feature,
  ResourceType.user,
];

export function* submitSearchWorker(action: SubmitSearchRequest): SagaIterator {
  const { searchTerm, useFilters } = action.payload;
  yield put(
    searchAll(
      searchTerm ? SearchType.SUBMIT_TERM : SearchType.CLEAR_TERM,
      searchTerm,
      ResourceType.table,
      0,
      useFilters
    )
  );
}
export function* submitSearchWatcher(): SagaIterator {
  yield takeLatest(SubmitSearch.REQUEST, submitSearchWorker);
}

/**
 * Handles workflow for any user action that causes an update to the search input for a given resource
 */
export function* submitSearchResourceWorker(
  action: SubmitSearchResourceRequest
): SagaIterator {
  const state = yield select(getSearchState);
  let { search_term, resource } = state;
  const { filters } = state;
  const { pageIndex, searchType, searchTerm, updateUrl } = action.payload;

  search_term = searchTerm !== undefined ? searchTerm : search_term;
  resource = action.payload.resource || resource;

  filters[resource] = action.payload.resourceFilters || filters[resource];
  yield put(searchResource(searchType, search_term, resource, pageIndex));

  if (updateUrl) {
    updateSearchUrl({
      filters,
      resource,
      term: search_term,
      index: pageIndex,
    });
  }
}
export function* submitSearchResourceWatcher(): SagaIterator {
  yield takeEvery(SubmitSearchResource.REQUEST, submitSearchResourceWorker);
}

/**
 * Handles workflow for any user action that causes an update to the search state.
 * Updates the search url if necessary.
 */
export function* updateSearchStateWorker(
  action: UpdateSearchStateRequest
): SagaIterator {
  if (action.payload !== undefined) {
    const { filters, resource, updateUrl, submitSearch } = action.payload;
    const state = yield select(getSearchState);
    if (filters && submitSearch) {
      yield put(searchAll(SearchType.FILTER, '', ResourceType.table, 0, true));
    } else if (updateUrl) {
      updateSearchUrl({
        resource: resource || state.resource,
        term: state.search_term,
        index: getPageIndex(state, resource),
        filters: filters || state.filters,
      });
    }
  }
}
export function* updateSearchStateWatcher(): SagaIterator {
  yield takeEvery(UpdateSearchState.REQUEST, updateSearchStateWorker);
}

/**
 * Handles workflow for handling url updates on the /search route.
 * Ensures that search state and and search results are updated based on url parameters.
 */
export function* urlDidUpdateWorker(action: UrlDidUpdateRequest): SagaIterator {
  const { urlSearch } = action.payload;
  const { term = '', resource, index, filters } = qs.parse(urlSearch);
  const parsedIndex = parseInt(index, 10);
  const parsedFilters = filters ? JSON.parse(filters) : null;

  const state = yield select(getSearchState);
  if (!!term && state.search_term !== term) {
    let updateUrl = false;
    if (parsedFilters) {
      updateUrl = true;
      yield put(
        updateSearchState({
          filters: {
            ...state.filters,
            [resource]: parsedFilters,
          },
        })
      );
    }
    yield put(
      searchAll(SearchType.LOAD_URL, term, resource, parsedIndex, updateUrl)
    );
  } else if (resource) {
    if (resource !== state.resource) {
      yield put(updateSearchState({ resource }));
    }

    if (parsedFilters && !isEqual(state.filters[resource], parsedFilters)) {
      yield put(
        submitSearchResource({
          resource,
          searchTerm: term,
          resourceFilters: parsedFilters,
          pageIndex: parsedIndex,
          searchType: SearchType.LOAD_URL,
        })
      );
    } else if (
      !isNaN(parsedIndex) &&
      parsedIndex !== getPageIndex(state, resource)
    ) {
      yield put(
        submitSearchResource({
          pageIndex: parsedIndex,
          searchType: SearchType.LOAD_URL,
        })
      );
    }
  }
}
export function* urlDidUpdateWatcher(): SagaIterator {
  yield takeEvery(UrlDidUpdate.REQUEST, urlDidUpdateWorker);
}

/**
 * Handles workflow for user actions on navigations components.
 * Leverages BrowserHistory or updates search url accordingly.
 */
export function* loadPreviousSearchWorker(): SagaIterator {
  const state = yield select(getSearchState);
  if (state.search_term === '') {
    BrowserHistory.goBack();
    return;
  }
  updateSearchUrl({
    term: state.search_term,
    resource: state.resource,
    index: getPageIndex(state),
    filters: state.filters,
  });
}
export function* loadPreviousSearchWatcher(): SagaIterator {
  yield takeEvery(LoadPreviousSearch.REQUEST, loadPreviousSearchWorker);
}

//  CORE SEARCH SAGAS
//  These sagas are not called directly by any components. They should be
//  called by other sagas as the final step for all use cases that will update
//  search results.

const computeSearchResourceResults = (resource, response) => {
  switch (resource) {
    case ResourceType.table:
      return { tables: response.table || initialState.tables };
    case ResourceType.user:
      return { users: response.user || initialState.users };
    case ResourceType.dashboard:
      return { dashboards: response.dashboard || initialState.dashboards };
    case ResourceType.feature:
      return { features: response.feature || initialState.features };
    default:
      return {};
  }
};

export function* searchResourceWorker(
  action: SearchResourceRequest
): SagaIterator {
  const { pageIndex, resource, term, searchType } = action.payload;
  const state = yield select(getSearchState);
  try {
    const response = yield call(
      API.search,
      pageIndex,
      getSearchResultsPerPage(),
      [resource],
      term,
      state.filters,
      searchType
    );
    const searchResourceResults = computeSearchResourceResults(
      resource,
      response
    );
    yield put(
      searchResourceSuccess({ search_term: term, ...searchResourceResults })
    );
  } catch (e) {
    yield put(searchResourceFailure());
  }
}
export function* searchResourceWatcher(): SagaIterator {
  yield takeEvery(SearchResource.REQUEST, searchResourceWorker);
}

export function* searchAllWorker(action: SearchAllRequest): SagaIterator {
  let { resource } = action.payload;
  const { pageIndex, term, useFilters, searchType } = action.payload;
  if (!useFilters) {
    yield put(updateSearchState({ filters: initialFilterState }));
  }
  const state = yield select(getSearchState);
  try {
    const response = yield call(
      API.search,
      pageIndex,
      getSearchResultsPerPage(),
      SEARCHABLE_RESOURCES,
      term,
      state.filters,
      searchType
    );
    const searchAllResponse = {
      resource,
      search_term: term,
      tables: response.table || initialState.tables,
      users: response.user || initialState.users,
      dashboards: response.dashboard || initialState.dashboards,
      features: response.feature || initialState.features,
      isLoading: false,
    };
    if (resource === undefined) {
      resource = autoSelectResource(searchAllResponse);
      searchAllResponse.resource = resource;
    }
    const index = getPageIndex(searchAllResponse);
    yield put(searchAllSuccess(searchAllResponse));
    updateSearchUrl({ term, resource, index, filters: state.filters }, true);
  } catch (e) {
    yield put(searchAllFailure());
  }
}
export function* searchAllWatcher(): SagaIterator {
  yield takeEvery(SearchAll.REQUEST, searchAllWorker);
}

//  INLINE SEARCH RESULTS SAGAS
//  These sagas support the inline search results feature.
//  TODO: Consider moving into nested directory similar to how filter logic.

export function* inlineSearchWorker(action: InlineSearchRequest): SagaIterator {
  const { term } = action.payload;
  try {
    const response = yield call(
      API.search,
      0,
      getSearchResultsPerPage(),
      SEARCHABLE_RESOURCES,
      term,
      {},
      SearchType.INLINE_SEARCH
    );
    const inlineSearchResponse = {
      dashboards: response.dashboard || initialInlineResultsState.dashboards,
      features: response.feature || initialInlineResultsState.features,
      tables: response.table || initialInlineResultsState.tables,
      users: response.user || initialInlineResultsState.users,
    };
    yield put(getInlineResultsSuccess(inlineSearchResponse));
  } catch (e) {
    yield put(getInlineResultsFailure());
  }
}
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
    yield put(
      searchAll(SearchType.INLINE_SELECT, searchTerm, resourceType, 0, false)
    );
    updateSearchUrl({ term: searchTerm, filters: state.search.filters });
  } else {
    if (updateUrl) {
      updateSearchUrl({
        resource: resourceType,
        term: searchTerm,
        index: 0,
        filters: state.search.filters,
      });
    }
    const data = {
      searchTerm,
      resource: resourceType,
      dashboards: state.search.inlineResults.dashboards,
      features: state.search.inlineResults.features,
      tables: state.search.inlineResults.tables,
      users: state.search.inlineResults.users,
    };
    yield put(updateFromInlineResult(data));
  }
}
export function* selectInlineResultsWatcher(): SagaIterator {
  yield takeEvery(InlineSearch.SELECT, selectInlineResultWorker);
}
