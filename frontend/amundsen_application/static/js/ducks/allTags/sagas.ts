import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import { metadataAllTags } from './api/v0';
import { GetAllTags } from './types';

export function* getAllTagsWorker(): SagaIterator {
  try {
    const tags = yield call(metadataAllTags);
    yield put({ type: GetAllTags.SUCCESS, payload: { tags }});
  } catch (e) {
    yield put({ type: GetAllTags.FAILURE, payload: { tags: [] }});
  }
}
export function* getAllTagsWatcher(): SagaIterator {
  yield takeEvery(GetAllTags.REQUEST, getAllTagsWorker);
}
