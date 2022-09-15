import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import * as API from './api/v0';
import { getFilterConfigSuccess, getFilterConfigFailure } from './reducer';

export enum GetFilterConfig {
  REQUEST = 'amundsen/filter_config/GET_FILTER_CONFIG_RESOURCE_REQUEST',
  SUCCESS = 'amundsen/filter_config/GET_FILTER_CONFIG_RESOURCE_SUCCESS',
  FAILED = 'amundsen/filter_config/GET_FILTER_CONFIG_RESOURCE_FAILED',
}

export function* getFilterConfigWorker(action): SagaIterator {
  try {
    const response = yield call(API.getFilterConfig);
    yield put(getFilterConfigSuccess(response));
  } catch (error) {
    yield put(getFilterConfigFailure(error));
  }
}

export function* getFilterConfigWatcher(): SagaIterator {
  yield takeEvery(GetFilterConfig.REQUEST, getFilterConfigWorker);
}
