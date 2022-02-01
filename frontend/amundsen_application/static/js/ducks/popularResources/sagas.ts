import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import * as API from './api/v0';
import {
  getPopularResourcesFailure,
  getPopularResourcesSuccess,
} from './reducer';
import { GetPopularResources, GetPopularResourcesRequest } from './types';

export function* getPopularResourcesWorker(
  action: GetPopularResourcesRequest
): SagaIterator {
  try {
    const { payload } = action;
    console.log('getPopularResourcesWorker', payload);
    const popularResources = yield call(
      API.getPopularResources,
      payload.userId
    );
    yield put(getPopularResourcesSuccess(popularResources));
  } catch (e) {
    yield put(getPopularResourcesFailure());
  }
}

export function* getPopularResourcesWatcher(): SagaIterator {
  yield takeEvery(GetPopularResources.REQUEST, getPopularResourcesWorker);
}
