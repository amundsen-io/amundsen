import { call, put, takeEvery } from 'redux-saga/effects';
import { SagaIterator } from 'redux-saga';

import {
  ExecuteSearch,
  ExecuteSearchRequest,
} from './reducer';

import {
  searchExecuteSearch,
} from '../api/search/v0';


export function* executeSearchWorker(action: ExecuteSearchRequest): SagaIterator {
  try {
    const searchResults = yield call(searchExecuteSearch, action);
    yield put({ type: ExecuteSearch.SUCCESS, payload: searchResults });
  } catch (e) {
    yield put({ type: ExecuteSearch.FAILURE });
  }
}

export function* executeSearchWatcher(): SagaIterator {
  yield takeEvery(ExecuteSearch.ACTION, executeSearchWorker);
}
