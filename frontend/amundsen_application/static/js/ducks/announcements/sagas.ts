import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import { announcementsGet } from './api/v0';
import { GetAnnouncements } from './types';

export function* getAnnouncementsWorker(): SagaIterator {
  try {
    const posts = yield call(announcementsGet);
    yield put({ type: GetAnnouncements.SUCCESS, payload: { posts } });
  } catch (e) {
    yield put({ type: GetAnnouncements.FAILURE, payload: { posts: [] } });
  }
}
export function* getAnnouncementsWatcher(): SagaIterator {
  yield takeEvery(GetAnnouncements.REQUEST, getAnnouncementsWorker);
}
