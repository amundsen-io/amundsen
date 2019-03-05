import { call, put, takeEvery } from 'redux-saga/effects';
import { SagaIterator } from 'redux-saga';

import { GetPopularTables, GetPopularTablesRequest } from './types';

import { metadataPopularTables} from './api/v0';

export function* getPopularTablesWorker(): SagaIterator {
  try {
    const popularTables = yield call(metadataPopularTables);
    yield put({ type: GetPopularTables.SUCCESS, payload: popularTables });
  } catch (e) {
    yield put({ type: GetPopularTables.FAILURE, payload: [] });
  }
}

export function* getPopularTablesWatcher(): SagaIterator {
  yield takeEvery(GetPopularTables.ACTION, getPopularTablesWorker);
}
