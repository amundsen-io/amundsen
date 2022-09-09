import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import * as API from './api/v0';
import { GetService } from './types';
import { getServiceSuccess, getServiceFailure } from './reducer';

export function* getServiceWorker(action): SagaIterator {
  try {
    const { key, index, source } = action.payload;
    const response = yield call(API.getService, key, index, source);
    yield put(getServiceSuccess(response));
  } catch (error) {
    yield put(getServiceFailure(error));
  }
}

export function* getServiceWatcher(): SagaIterator {
  yield takeEvery(GetService.REQUEST, getServiceWorker);
}
