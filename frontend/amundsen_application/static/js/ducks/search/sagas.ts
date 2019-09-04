import { SagaIterator } from 'redux-saga';
import { all, call, put, select, takeEvery } from 'redux-saga/effects';
import * as qs from 'simple-query-string';

import { ResourceType } from 'interfaces/Resources';

import * as API from './api/v0';

import {
  LoadPreviousSearch,
  LoadPreviousSearchRequest,
  SearchAll,
  SearchAllRequest,
  SearchResource,
  SearchResourceRequest,
  SetPageIndex,
  SetPageIndexRequest, SetResource, SetResourceRequest,
  SubmitSearch,
  SubmitSearchRequest,
  UrlDidUpdate,
  UrlDidUpdateRequest,
} from './types';

import {
  initialState,
  searchAll,
  searchAllFailure,
  searchAllSuccess,
  searchResource,
  searchResourceFailure,
  searchResourceSuccess, setPageIndex, setResource,
} from './reducer';
import { getPageIndex, getSearchState } from './utils';
import { updateSearchUrl } from 'utils/navigation-utils';

export function* searchAllWorker(action: SearchAllRequest): SagaIterator {
  const { resource, pageIndex, term } = action.payload;
  const tableIndex = resource === ResourceType.table ? pageIndex : 0;
  const userIndex = resource === ResourceType.user ? pageIndex : 0;
  const dashboardIndex = resource === ResourceType.dashboard ? pageIndex : 0;

  try {
    const [tableResponse, userResponse, dashboardResponse] = yield all([
      call(API.searchResource, tableIndex, ResourceType.table, term),
      call(API.searchResource, userIndex, ResourceType.user, term),
      call(API.searchResource, dashboardIndex, ResourceType.dashboard, term),
    ]);
    const searchAllResponse = {
      search_term: term,
      selectedTab: resource,
      tables: tableResponse.tables || initialState.tables,
      users: userResponse.users || initialState.users,
      dashboards: dashboardResponse.dashboards || initialState.dashboards,
      isLoading: false,
    };
    const index = getPageIndex(searchAllResponse, resource);
    yield put(searchAllSuccess(searchAllResponse));
    updateSearchUrl({ term, resource, index, }, true);

  } catch (e) {
    yield put(searchAllFailure());
  }
};
export function* searchAllWatcher(): SagaIterator {
  yield takeEvery(SearchAll.REQUEST, searchAllWorker);
};

export function* searchResourceWorker(action: SearchResourceRequest): SagaIterator {
  const { pageIndex, resource, term } = action.payload;
  try {
    const searchResults = yield call(API.searchResource, pageIndex, resource, term);
    yield put(searchResourceSuccess(searchResults));
  } catch (e) {
    yield put(searchResourceFailure());
  }
};
export function* searchResourceWatcher(): SagaIterator {
  yield takeEvery(SearchResource.REQUEST, searchResourceWorker);
};

export function* submitSearchWorker(action: SubmitSearchRequest): SagaIterator {
  const { searchTerm } = action.payload;
  yield put(searchAll(searchTerm, ResourceType.table, 0));
  updateSearchUrl({ term: searchTerm });
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
    });
  }
};
export function* setResourceWatcher(): SagaIterator {
  yield takeEvery(SetResource.REQUEST, setResourceWorker);
};

export function* setPageIndexWorker(action: SetPageIndexRequest): SagaIterator {
  const { pageIndex, updateUrl } = action.payload;
  const state = yield select(getSearchState);
  yield put(searchResource(state.search_term, state.selectedTab, pageIndex));

  if (updateUrl) {
    updateSearchUrl({
      term: state.search_term,
      resource: state.selectedTab,
      index: pageIndex,
    });
  }
};
export function* setPageIndexWatcher(): SagaIterator {
  yield takeEvery(SetPageIndex.REQUEST, setPageIndexWorker);
};

export function* urlDidUpdateWorker(action: UrlDidUpdateRequest): SagaIterator {
  const { urlSearch } = action.payload;
  const { term, resource, index} = qs.parse(urlSearch);
  const parsedIndex = parseInt(index, 10);

  const state = yield select(getSearchState);
  if (!!term && state.search_term !== term) {
    yield put(searchAll(term, resource, parsedIndex));
  } else if (!!resource && resource !== state.selectedTab) {
    yield put(setResource(resource, false))
  } else if (!isNaN(parsedIndex) && parsedIndex !== getPageIndex(state, resource)) {
    yield put(setPageIndex(parsedIndex, false));
  }
};
export function* urlDidUpdateWatcher(): SagaIterator {
  yield takeEvery(UrlDidUpdate.REQUEST, urlDidUpdateWorker);
};

export function* loadPreviousSearchWorker(action: LoadPreviousSearchRequest): SagaIterator {
  const state = yield select(getSearchState);
  updateSearchUrl({
    term: state.search_term,
    resource: state.selectedTab,
    index: getPageIndex(state, state.selectedTab),
  });
};
export function* loadPreviousSearchWatcher(): SagaIterator {
  yield takeEvery(LoadPreviousSearch.REQUEST, loadPreviousSearchWorker);
};
