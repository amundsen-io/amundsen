import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import * as API from './api/v0';
import { getFeatureSuccess, getFeatureFailure } from './reducer';
import { GetFeature } from './types';

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
