import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';
import { announcementsGet } from '../api/announcements/v0';
import { AnnouncementsGet, AnnouncementsGetRequest } from "./reducer";


export function* announcementsGetWorker(action: AnnouncementsGetRequest): SagaIterator {
  try {
    const announcements = yield call(announcementsGet);
    yield put({ type: AnnouncementsGet.SUCCESS, payload: announcements });
  } catch(error) {
    yield put({ type: AnnouncementsGet.FAILURE });
  }
}

export function* announcementsGetWatcher(): SagaIterator {
  yield takeEvery(AnnouncementsGet.ACTION, announcementsGetWorker);
}
