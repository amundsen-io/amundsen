import { SagaIterator } from 'redux-saga';
import { all, call, put, select, takeEvery } from 'redux-saga/effects';

import { UpdateTags, UpdateTagsRequest } from '../types';

import { metadataUpdateTableTags, metadataTableTags } from '../api/v0';

export function* updateTableTagsWorker(action: UpdateTagsRequest): SagaIterator {
  const state = yield select();
  const tableData = state.tableMetadata.tableData;
  try {
    yield all(metadataUpdateTableTags(action.payload.tagArray, tableData.key));
    const newTags = yield call(metadataTableTags, tableData.key);
    yield put({ type: UpdateTags.SUCCESS, payload: { tags: newTags } });
  } catch (e) {
    yield put({ type: UpdateTags.FAILURE, payload: { tags: [] } });
  }
};
export function* updateTableTagsWatcher(): SagaIterator {
  yield takeEvery(UpdateTags.REQUEST, updateTableTagsWorker);
};
