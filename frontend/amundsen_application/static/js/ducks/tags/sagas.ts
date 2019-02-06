import { call, put, takeEvery } from 'redux-saga/effects';
import { SagaIterator } from 'redux-saga';

import {
  GetAllTags,
} from './reducer';

import {
  metadataAllTags,
} from '../api/metadata/v0';

export function* getAllTagsWorker(): SagaIterator {
  try {
    const tags = yield call(metadataAllTags);
    yield put({ type: GetAllTags.SUCCESS, payload: tags });
  } catch (e) {
    yield put({ type: GetAllTags.FAILURE, payload: [] });
  }
}

export function* getAllTagsWatcher(): SagaIterator {
  yield takeEvery(GetAllTags.ACTION, getAllTagsWorker);
}
