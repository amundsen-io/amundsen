import { SagaIterator } from 'redux-saga';
import { all, call, put, takeEvery } from 'redux-saga/effects';

import {
  getSnowflakeTableSharesFailure,
  getSnowflakeTableSharesSuccess
} from './reducer';

import * as API from './api/v0';

import { GetSnowflakeTableShares, GetSnowflakeTableSharesRequest } from './types';

export function* getSnowflakeTableSharesWorker(action: GetSnowflakeTableSharesRequest): SagaIterator {
  const { tableUri } = action.payload;
  try {
    const snowflakeTableShares = yield call(API.getSnowflakeTableShares, tableUri);
    
    yield put(getSnowflakeTableSharesSuccess(snowflakeTableShares));
  } catch (e) {
    yield put(getSnowflakeTableSharesFailure());
  }
}
export function* getSnowflakeTableSharesWatcher(): SagaIterator {
  yield takeEvery(GetSnowflakeTableShares.REQUEST, getSnowflakeTableSharesWorker);
}
