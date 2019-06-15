import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import { metadataPopularTables} from './api/v0';

import { GetPopularTables } from './types';

export function* getPopularTablesWorker(): SagaIterator {
  try {
    const popularTables = yield call(metadataPopularTables);
    yield put({ type: GetPopularTables.SUCCESS, payload: { tables: popularTables } });
  } catch (e) {
    yield put({ type: GetPopularTables.FAILURE, payload: { tables: [] } });
  }
}

export function* getPopularTablesWatcher(): SagaIterator {
  yield takeEvery(GetPopularTables.REQUEST, getPopularTablesWorker);
}
