import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import * as API from './api/v0';
import { GetAppEvent } from './types';
import { getAppEventSuccess, getAppEventFailure } from './reducer';

export function* getAppEventWorker(action): SagaIterator {
  try {
    const { key, index, source } = action.payload;
    const response = yield call(API.getAppEvent, key, index, source);
    yield put(getAppEventSuccess(response));
  } catch (error) {
    yield put(getAppEventFailure(error));
  }
}

export function* getAppEventWatcher(): SagaIterator {
  yield takeEvery(GetAppEvent.REQUEST, getAppEventWorker);
}
