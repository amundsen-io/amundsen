import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import * as API from './api/v0';
import {
  getFeatureSuccess,
  getFeatureFailure,
  getFeatureCodeSuccess,
  getFeatureCodeFailure,
} from './reducer';
import { GetFeature, GetFeatureCode } from './types';

export function* getFeatureWorker(action): SagaIterator {
  try {
    const { key, index, source } = action.payload;
    const response = yield call(API.getFeature, key, index, source);
    yield put(getFeatureSuccess(response));
  } catch (error) {
    yield put(getFeatureFailure(error));
  }
}
export function* getFeatureWatcher(): SagaIterator {
  yield takeEvery(GetFeature.REQUEST, getFeatureWorker);
}

export function* getFeatureCodeWorker(action): SagaIterator {
  try {
    const { key } = action.payload;
    const response = yield call(API.getFeatureCode, key);
    yield put(getFeatureCodeSuccess(response));
  } catch (error) {
    yield put(getFeatureCodeFailure(error));
  }
}
export function* getFeatureCodeWatcher(): SagaIterator {
  yield takeEvery(GetFeatureCode.REQUEST, getFeatureCodeWorker);
}
