import { SagaIterator } from 'redux-saga';
import { call, put, select, takeEvery, takeLatest } from 'redux-saga/effects';

import * as API from './api/v0';

import {
  getProviderDataFailure,
  getProviderDataSuccess,
  getProviderDescriptionFailure,
  getProviderDescriptionSuccess,
} from './reducer';

import {
  GetProviderData,
  GetProviderDataRequest,
  GetProviderDescription,
  GetProviderDescriptionRequest,
  UpdateProviderDescription,
  UpdateProviderDescriptionRequest,
} from './types';

export function* getProviderDataWorker(action: GetProviderDataRequest): SagaIterator {
  const { key, searchIndex, source } = action.payload;

  try {
    console.log(`getProviderDataWorker`);
    const { data, statusCode, tags } = yield call(
      API.getProviderData,
      key,
      searchIndex,
      source
    );

    yield put(getProviderDataSuccess(data, statusCode, tags));
  } catch (e) {
    yield put(getProviderDataFailure());
  }
}
export function* getProviderDataWatcher(): SagaIterator {
  console.log(`getProviderDataWatcher`);
  yield takeEvery(GetProviderData.REQUEST, getProviderDataWorker);
}

export function* getProviderDescriptionWorker(
  action: GetProviderDescriptionRequest
): SagaIterator {
  const { payload } = action;
  const state = yield select();
  let { providerData } = state.providerMetadata;

  try {
    // TODO - Cleanup this pattern of sending in the provider metadata and then modifying it and sending it back.
    // Should just fetch the description and send it back to the reducer.
    providerData = yield call(
      API.getProviderDescription,
      state.providerMetadata.providerData
    );
    yield put(getProviderDescriptionSuccess(providerData));
    if (payload.onSuccess) {
      yield call(payload.onSuccess);
    }
  } catch (e) {
    yield put(getProviderDescriptionFailure(providerData));
    if (payload.onFailure) {
      yield call(payload.onFailure);
    }
  }
}
export function* getProviderDescriptionWatcher(): SagaIterator {
  yield takeEvery(GetProviderDescription.REQUEST, getProviderDescriptionWorker);
}

export function* updateProviderDescriptionWorker(
  action: UpdateProviderDescriptionRequest
): SagaIterator {
  const { payload } = action;
  const state = yield select();

  try {
    yield call(
      API.updateProviderDescription,
      payload.newValue,
      state.providerMetadata.providerData
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
export function* updateProviderDescriptionWatcher(): SagaIterator {
  yield takeEvery(UpdateProviderDescription.REQUEST, updateProviderDescriptionWorker);
}
