import { call, put, takeEvery } from 'redux-saga/effects';
import { SagaIterator } from 'redux-saga';

import {
  SearchAll,
  SearchAllRequest,
  SearchResource,
  SearchResourceRequest,
} from './types';

import {
  searchAll, searchResource,
} from './api/v0';


// SearchAll
export function* searchAllWorker(action: SearchAllRequest): SagaIterator {
  try {
    const searchResults = yield call(searchAll, action);
    yield put({ type: SearchAll.SUCCESS, payload: searchResults });
  } catch (e) {
    yield put({ type: SearchAll.FAILURE });
  }
}

export function* searchAllWatcher(): SagaIterator {
  yield takeEvery(SearchAll.ACTION, searchAllWorker);
}


// SearchResource
export function* searchResourceWorker(action: SearchResourceRequest): SagaIterator {
  try {
    const searchResults = yield call(searchResource, action);
    yield put({ type: SearchResource.SUCCESS, payload: searchResults });
  } catch (e) {
    yield put({ type: SearchResource.FAILURE });
  }
}

export function* searchResourceWatcher(): SagaIterator {
  yield takeEvery(SearchResource.ACTION, searchResourceWorker);
}
