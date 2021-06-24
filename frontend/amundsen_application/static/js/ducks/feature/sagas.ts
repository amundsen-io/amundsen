import { SagaIterator } from 'redux-saga';
import { call, put, select, takeEvery } from 'redux-saga/effects';

import * as API from './api/v0';
import {
  getFeatureSuccess,
  getFeatureFailure,
  getFeatureCodeSuccess,
  getFeatureCodeFailure,
  getFeatureDescriptionSuccess,
  getFeatureDescriptionFailure,
} from './reducer';

import {
  GetFeature,
  GetFeatureCode,
  GetFeatureDescription,
  GetFeatureDescriptionRequest,
  UpdateFeatureDescription,
  UpdateFeatureDescriptionRequest,
} from './types';

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
export function* getFeatureDescriptionWorker(
  action: GetFeatureDescriptionRequest
): SagaIterator {
  const { payload } = action;
  const state = yield select();
  const { feature } = state.feature;
  let { description } = feature;
  try {
    description = yield call(API.getFeatureDescription, feature.key);
    yield put(getFeatureDescriptionSuccess(description));
    if (payload.onSuccess) {
      yield call(payload.onSuccess);
    }
  } catch (e) {
    yield put(getFeatureDescriptionFailure(description));
    if (payload.onFailure) {
      yield call(payload.onFailure);
    }
  }
}
export function* getFeatureDescriptionWatcher(): SagaIterator {
  yield takeEvery(GetFeatureDescription.REQUEST, getFeatureDescriptionWorker);
}

export function* updateFeatureDescriptionWorker(
  action: UpdateFeatureDescriptionRequest
): SagaIterator {
  const { payload } = action;
  const state = yield select();
  try {
    yield call(
      API.updateFeatureDescription,
      state.feature.feature.key,
      payload.newValue
    );
    if (payload.onSuccess) {
      yield call(payload.onSuccess);
    }
  } catch (e) {
    if (payload.onFailure) {
      yield call(payload.onFailure);
    }
  }
}
export function* updateFeatureDescriptionWatcher(): SagaIterator {
  yield takeEvery(
    UpdateFeatureDescription.REQUEST,
    updateFeatureDescriptionWorker
  );
}
