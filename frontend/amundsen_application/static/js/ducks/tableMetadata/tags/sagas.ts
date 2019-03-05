import { all, call, put, select, takeEvery } from 'redux-saga/effects';
import { SagaIterator } from 'redux-saga';

import { UpdateTags, UpdateTagsRequest } from '../types';

import { metadataUpdateTableTags, metadataTableTags } from '../api/v0';

// updateTags
export function* updateTableTagsWorker(action: UpdateTagsRequest): SagaIterator {
  const state = yield select();
  const tableData = state.tableMetadata.tableData;
  try {
    yield all(metadataUpdateTableTags(action, tableData));
    const newTags = yield call(metadataTableTags, tableData);
    yield put({ type: UpdateTags.SUCCESS, payload: newTags });
  } catch (e) {
    yield put({ type: UpdateTags.FAILURE, payload: [] });
  }
}

export function* updateTableTagsWatcher(): SagaIterator {
  yield takeEvery(UpdateTags.ACTION, updateTableTagsWorker);
}
