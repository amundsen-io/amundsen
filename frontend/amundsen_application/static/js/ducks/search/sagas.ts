import { SagaIterator } from 'redux-saga';
import { all, call, put, takeEvery } from 'redux-saga/effects';

import {
  SearchAll,
  SearchAllRequest,
  SearchResource,
  SearchResourceRequest,
} from './types';

import {
  searchResource,
} from './api/v0';
import { ResourceType } from 'interfaces/Resources';

import {
  searchAllSuccess, searchAllFailure,
  searchResourceSuccess, searchResourceFailure,
} from './reducer';

export function* searchAllWorker(action: SearchAllRequest): SagaIterator {
  const { options, term } = action.payload;
  try {
    const [tableResponse, userResponse, dashboardResponse] = yield all([
      call(searchResource, options.tableIndex, ResourceType.table, term),
      call(searchResource, options.userIndex, ResourceType.user, term),
      call(searchResource, options.dashboardIndex, ResourceType.dashboard, term),
    ]);
    const searchAllResponse = {
      search_term: term,
      tables: tableResponse.tables,
      users: userResponse.users,
      dashboards: dashboardResponse.dashboards,
    };
    yield put({ type: SearchAll.SUCCESS, payload: searchAllResponse });
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
    const searchResults = yield call(searchResource, pageIndex, resource, term);
    yield put(searchResourceSuccess(searchResults));
  } catch (e) {
    yield put(searchResourceFailure());
  }
}
export function* searchResourceWatcher(): SagaIterator {
  yield takeEvery(SearchResource.REQUEST, searchResourceWorker);
}
