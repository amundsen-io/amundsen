import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import * as API from './api/v0';
import { getAnnouncementsFailure, getAnnouncementsSuccess } from './reducer';
import { GetAnnouncements } from './types';

export function* getAnnouncementsWorker(): SagaIterator {
  try {
    const posts = yield call(API.getAnnouncements);
    yield put(getAnnouncementsSuccess(posts));
  } catch (e) {
    yield put(getAnnouncementsFailure());
  }
}
export function* getAnnouncementsWatcher(): SagaIterator {
  yield takeEvery(GetAnnouncements.REQUEST, getAnnouncementsWorker);
}
