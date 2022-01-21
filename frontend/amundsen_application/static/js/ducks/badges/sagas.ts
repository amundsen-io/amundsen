// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import { getAllBadgesSuccess, getAllBadgesFailure } from './reducer';

import * as API from './api/v0';

import { GetAllBadges } from './types';

export function* getAllBadgesWorker(): SagaIterator {
  try {
    const allBadges = yield call(API.getAllBadges);
    yield put(getAllBadgesSuccess(allBadges));
  } catch (e) {
    yield put(getAllBadgesFailure());
  }
}
export function* getAllBadgesWatcher(): SagaIterator {
  yield takeEvery(GetAllBadges.REQUEST, getAllBadgesWorker);
}
