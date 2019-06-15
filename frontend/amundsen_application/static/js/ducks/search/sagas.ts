import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import {
  SearchAll,
  SearchAllRequest,
  SearchResource,
  SearchResourceRequest,
} from './types';

import {
  searchAll, searchResource,
} from './api/v0';

export function* searchAllWorker(action: SearchAllRequest): SagaIterator {
  const { options, term } = action;
  try {
    const searchResults = yield call(searchAll, options, term);
    yield put({ type: SearchAll.SUCCESS, payload: searchResults });
  } catch (e) {
    yield put({ type: SearchAll.FAILURE });
  }
};
export function* searchAllWatcher(): SagaIterator {
  yield takeEvery(SearchAll.REQUEST, searchAllWorker);
};

export function* searchResourceWorker(action: SearchResourceRequest): SagaIterator {
  const { pageIndex, resource, term } = action;
  try {
    const searchResults = yield call(searchResource, pageIndex, resource, term);
    yield put({ type: SearchResource.SUCCESS, payload: searchResults });
  } catch (e) {
    yield put({ type: SearchResource.FAILURE });
  }
}
export function* searchResourceWatcher(): SagaIterator {
  yield takeEvery(SearchResource.REQUEST, searchResourceWorker);
}
