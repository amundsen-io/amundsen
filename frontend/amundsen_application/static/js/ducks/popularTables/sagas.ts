import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import * as API from './api/v0';
import { getPopularTablesFailure, getPopularTablesSuccess } from './reducer';
import { GetPopularTables } from './types';

export function* getPopularTablesWorker(): SagaIterator {
  try {
    const popularTables = yield call(API.getPopularTables);
    yield put(getPopularTablesSuccess(popularTables));
  } catch (e) {
    yield put(getPopularTablesFailure());
  }
}

export function* getPopularTablesWatcher(): SagaIterator {
  yield takeEvery(GetPopularTables.REQUEST, getPopularTablesWorker);
}
