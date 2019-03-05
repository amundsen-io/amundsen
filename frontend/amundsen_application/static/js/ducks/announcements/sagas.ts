import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import { announcementsGet } from './api/v0';

import { AnnouncementsGet } from './types';

export function* announcementsGetWorker(): SagaIterator {
  try {
    const announcements = yield call(announcementsGet);
    yield put({ type: AnnouncementsGet.SUCCESS, payload: announcements });
  } catch(error) {
    yield put({ type: AnnouncementsGet.FAILURE, payload: [] });
  }
}

export function* announcementsGetWatcher(): SagaIterator {
  yield takeEvery(AnnouncementsGet.ACTION, announcementsGetWorker);
}
