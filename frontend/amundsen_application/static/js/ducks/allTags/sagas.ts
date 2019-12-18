import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import * as API from './api/v0';
import { getAllTagsFailure, getAllTagsSuccess } from './reducer';
import { GetAllTags } from './types';

export function* getAllTagsWorker(): SagaIterator {
  try {
    const allTags = yield call(API.getAllTags);

    yield put(getAllTagsSuccess(allTags));
  } catch (e) {
    yield put(getAllTagsFailure());
  }
}
export function* getAllTagsWatcher(): SagaIterator {
  yield takeEvery(GetAllTags.REQUEST, getAllTagsWorker);
}
